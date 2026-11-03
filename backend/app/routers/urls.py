import secrets
import string
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.url import URLMapping
from app.models.click import ClickEvent
from app.schemas.url import (
    ShortenURLRequest,
    ShortenURLResponse,
    URLItemResponse,
)
from app.security.url_validator import validate_and_sanitize_url, validate_custom_alias, URLSecurityError
from app.security.auth import get_token_claims, get_optional_token_claims, verify_resource_ownership
from app.security.rate_limiter import check_rate_limit, get_client_ip
from app.services.analytics import extract_click_metadata

router = APIRouter(tags=["URLs & Redirection"])


def generate_short_code(length: int = 7) -> str:
    """Generates a random Base62 alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


@router.post(
    "/shorten",
    response_model=ShortenURLResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_rate_limit)],
    summary="Shorten a long destination URL with security validation and rate limiting"
)
def shorten_url(
    payload: ShortenURLRequest,
    request: Request,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_token_claims),
    db: Session = Depends(get_db)
):
    """
    Core URL Shortening endpoint:
    - Applies tiered rate limits (10/hr anonymous, 100/hr registered, 10,000/hr premium).
    - Validates protocol (HTTP/HTTPS only).
    - Prevents SSRF attacks (blocks localhost, 127.0.0.1, 169.254.169.254, RFC1918 private IPs).
    - Enforces custom alias sanitization and reserved-route defense.
    - Associates link with authenticated user if logged in.
    """
    # 1. Validate destination URL
    try:
        # check_dns=False during mock unit tests, True in production
        validated_url = validate_and_sanitize_url(payload.long_url, check_dns=True)
    except URLSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 2. Determine short code
    if payload.custom_alias:
        try:
            short_code = validate_custom_alias(payload.custom_alias)
        except URLSecurityError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # Check collision
        existing = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The alias '{short_code}' is already taken."
            )
    else:
        # Generate unique code with retry
        for _ in range(5):
            candidate = generate_short_code()
            if not db.query(URLMapping).filter(URLMapping.short_code == candidate).first():
                short_code = candidate
                break
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to allocate unique short code.")

    # 3. Associate creator
    user_id = claims.get("sub") if claims else None

    mapping = URLMapping(
        short_code=short_code,
        original_url=validated_url,
        expires_at=payload.expires_at,
        created_by=user_id,
        created_at=datetime.utcnow()
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{mapping.short_code}"

    return ShortenURLResponse(
        short_url=short_url,
        short_code=mapping.short_code,
        long_url=mapping.original_url,
        created_at=mapping.created_at,
        expires_at=mapping.expires_at
    )


@router.get(
    "/urls",
    response_model=List[URLItemResponse],
    summary="List URLs owned by the authenticated user"
)
def list_user_urls(
    claims: Dict[str, Any] = Depends(get_token_claims),
    db: Session = Depends(get_db)
):
    """
    Enforces user ownership: only returns URLs created by the caller's user ID.
    """
    user_id = claims.get("sub")
    urls = (
        db.query(URLMapping)
        .filter(URLMapping.created_by == user_id)
        .order_by(URLMapping.created_at.desc())
        .all()
    )

    items = []
    for u in urls:
        clicks = db.query(func.count(ClickEvent.id)).filter(ClickEvent.url_mapping_id == u.id).scalar() or 0
        items.append(
            URLItemResponse(
                id=u.id,
                short_code=u.short_code,
                long_url=u.original_url,
                created_at=u.created_at,
                expires_at=u.expires_at,
                created_by=u.created_by,
                click_count=clicks
            )
        )
    return items


@router.delete(
    "/urls/{url_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a URL with ownership verification"
)
def delete_user_url(
    url_id: str,
    claims: Dict[str, Any] = Depends(get_token_claims),
    db: Session = Depends(get_db)
):
    """
    Enforces strict object-level authorization (IDOR protection):
    Users can only delete their own URLs. Admins can delete any.
    """
    url_mapping = db.query(URLMapping).filter(URLMapping.id == url_id).first()
    if not url_mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found.")

    current_user_id = claims.get("sub")
    is_admin = claims.get("tier") == "admin"

    # Enforce ownership
    verify_resource_ownership(url_mapping.created_by, current_user_id, is_admin)

    db.delete(url_mapping)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

