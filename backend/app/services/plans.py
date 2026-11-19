from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status


MAX_LINK_DAYS = {
    "free": 10,
    "registered": 10,  # Legacy tier name
    "plus": 30,
    "pro": None,
    "premium": None,  # Legacy tier name
    "admin": None,
}


def normalize_tier(tier: Optional[str]) -> str:
    if tier in {"plus", "pro", "admin"}:
        return tier
    if tier == "premium":
        return "pro"
    return "free"


def resolve_link_expiration(
    tier: str,
    expires_in_days: Optional[int],
    requested_expires_at: Optional[datetime],
) -> Optional[datetime]:
    """Apply the plan's maximum lifetime on the server, regardless of UI input."""
    if expires_in_days is not None and requested_expires_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Choose a link duration or an expiration date, not both.",
        )

    max_days = MAX_LINK_DAYS[normalize_tier(tier)]
    now = datetime.utcnow()

    if expires_in_days is not None:
        if expires_in_days == 0:
            if max_days is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="A link with no expiration is available on the Pro plan.",
                )
            return None
        if expires_in_days < 1 or (max_days is not None and expires_in_days > max_days):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your {normalize_tier(tier).title()} plan allows links for up to {max_days} days.",
            )
        return now + timedelta(days=expires_in_days)

    if requested_expires_at is not None:
        expiration = requested_expires_at
        if expiration.tzinfo is not None:
            expiration = expiration.astimezone(timezone.utc).replace(tzinfo=None)
        if expiration <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expiration date must be in the future.",
            )
        if max_days is not None and expiration > now + timedelta(days=max_days):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your {normalize_tier(tier).title()} plan allows links for up to {max_days} days.",
            )
        return expiration

    return None if max_days is None else now + timedelta(days=max_days)
