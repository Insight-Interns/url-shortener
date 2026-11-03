from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

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

# Startup handler to initialize tables safely
@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Logs warning if DB server is not reachable yet
        print(f"[Warning] Database initialization skipped or deferred: {e}")

# 1. Mount Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "Retry-After"],
)

# 3. Mount Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(urls_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


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
    Public URL Redirection Endpoint:
    - Resolves short code.
    - Verifies link has not expired.
    - Asynchronously logs privacy-preserving click analytics (hashed IP, device, referrer).
    - Issues HTTP 307 redirection to destination.
    """
    mapping = db.query(URLMapping).filter(URLMapping.short_code == code).first()
    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found.")

    # Expiry verification
    if mapping.expires_at and mapping.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This short link has expired."
        )

    # Privacy-preserving click tracking
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")

    meta = extract_click_metadata(client_ip, user_agent, referrer)
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

    return RedirectResponse(url=mapping.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
