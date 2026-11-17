
import secrets
import string
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
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
from app.security.url_validator import (
    validate_and_sanitize_url,
    validate_custom_alias,
    URLSecurityError
)
from app.security.auth import (
    get_token_claims,
    get_optional_token_claims,
    verify_resource_ownership
)
from app.security.rate_limiter import check_rate_limit


router = APIRouter(tags=["URLs & Redirection"])


def generate_short_code(length: int = 7) -> str:
    """Generate a cryptographically secure Base62 short code."""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def normalize_expiration(expiration: Optional[datetime]) -> Optional[datetime]:
    """Normalize expiration timestamps to UTC-naive datetime."""
    if expiration is None:
        return None

    if expiration.tzinfo is not None:
        expiration = expiration.astimezone(
            timezone.utc
        ).replace(tzinfo=None)

    return expiration


@router.post(
    "/shorten",
    response_model=ShortenURLResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_rate_limit)],
    summary="Shorten a long destination URL"
)
def shorten_url(
    payload: ShortenURLRequest,
    request: Request,
    claims: Optional[Dict[str, Any]] = Depends(get_optional_token_claims),
    db: Session = Depends(get_db)
):
    """Validate, create and store a shortened URL."""

    # 1. Validate destination URL
    try:
        validated_url = validate_and_sanitize_url(
            payload.long_url,
            check_dns=True
        )
    except URLSecurityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 2. Validate expiration date
    expiration = normalize_expiration(payload.expires_at)

    if expiration and expiration <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expiration date must be in the future."
        )

    # 3. Determine short code
    if payload.custom_alias:
        try:
            short_code = validate_custom_alias(payload.custom_alias)
        except URLSecurityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        existing = (
            db.query(URLMapping)
            .filter(URLMapping.short_code == short_code)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The alias '{short_code}' is already taken."
            )

    else:
        short_code = None 

        for _ in range(5):
            candidate = generate_short_code()

            existing = (
                db.query(URLMapping)
                .filter(URLMapping.short_code == candidate)
                .first()
            )

            if not existing:
                short_code = candidate
                break

        if short_code is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to allocate unique short code."
            )

    # 4. Associate creator
    user_id = claims.get("sub") if claims else None

    # 5. Create database mapping
    mapping = URLMapping(
        short_code=short_code,
        original_url=validated_url,
        expires_at=expiration,
        created_by=user_id,
        created_at=datetime.utcnow()
    )

    # 6. Save mapping with transaction safety
    try:
        db.add(mapping)
        db.commit()
        db.refresh(mapping)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the shortened URL."
        )

    # 7. Generate short URL
    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{mapping.short_code}"

    # 8. Return response
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
    """Return URLs belonging to the authenticated user."""

    user_id = claims.get("sub")

    urls = (
        db.query(URLMapping)
        .filter(URLMapping.created_by == user_id)
        .order_by(URLMapping.created_at.desc())
        .all()
    )

    items = []

    for url in urls:
        clicks = (
            db.query(func.count(ClickEvent.id))
            .filter(ClickEvent.url_mapping_id == url.id)
            .scalar() or 0
        )

        items.append(
            URLItemResponse(
                id=url.id,
                short_code=url.short_code,
                long_url=url.original_url,
                created_at=url.created_at,
                expires_at=url.expires_at,
                created_by=url.created_by,
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
    """Delete a URL after verifying ownership."""

    url_mapping = (
        db.query(URLMapping)
        .filter(URLMapping.id == url_id)
        .first()
    )

    if not url_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found."
        )

    current_user_id = claims.get("sub")
    is_admin = claims.get("tier") == "admin"

    verify_resource_ownership(
        url_mapping.created_by,
        current_user_id,
        is_admin
    )

    try:
        db.delete(url_mapping)
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the URL."
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
