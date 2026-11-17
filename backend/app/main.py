
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, status, Request  # type: ignore[import-not-found]
from fastapi.responses import RedirectResponse  # type: ignore[import-not-found]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
from sqlalchemy.orm import Session  # type: ignore[import-not-found]

from app.core.config import settings
from app.db.session import get_db, Base, engine
from app.models.url import URLMapping
from app.models.click import ClickEvent
from app.security.headers import SecurityHeadersMiddleware
from app.security.rate_limiter import get_client_ip
from app.services.analytics import extract_click_metadata
from app.routers.auth import router as auth_router
from app.routers.urls import router as urls_router
from app.routers.analytics import router as analytics_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[Warning] Database initialization skipped or deferred: {e}")


# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "Retry-After"
    ],
)


# Register API routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(urls_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["System"])
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1": settings.API_V1_STR,
        "message": "URL Shortener API is running. Visit /docs for interactive Swagger documentation."
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get(
    "/{code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    tags=["Redirection"]
)
def redirect_short_url(
    code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Resolves a short code and redirects to the original URL.

    Analytics failures must not prevent a valid redirect.
    """

    # 1. Retrieve URL mapping
    mapping = (
        db.query(URLMapping)
        .filter(URLMapping.short_code == code)
        .first()
    )

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short code not found."
        )

    # 2. Check expiration
    if mapping.expires_at:
        expiration = mapping.expires_at

        if expiration.tzinfo is not None:
            expiration = expiration.astimezone(
                timezone.utc
            ).replace(tzinfo=None)

        if expiration <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="This short link has expired."
            )

    # 3. Record click analytics independently
    try:
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent")
        referrer = request.headers.get("referer")

        meta = extract_click_metadata(
            client_ip,
            user_agent,
            referrer
        )

        click_event = ClickEvent(
            url_mapping_id=mapping.id,
            ip_hash=meta["ip_hash"],
            user_agent=meta["user_agent"],
            referrer=meta["referrer"],
            device_type=meta["device_type"],
            country_code=meta["country_code"],
            clicked_at=meta["clicked_at"]
        )

        db.add(click_event)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"[Warning] Click analytics recording failed: {e}")

    # 4. Redirect to original destination
    return RedirectResponse(
        url=mapping.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
