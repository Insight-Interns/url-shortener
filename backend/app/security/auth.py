import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt

try:
    import jwt  # type: ignore
except ImportError:
    from jose import jwt  # type: ignore  # fallback for python-jose environments

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


class AuthSecurityError(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


def validate_password_strength(password: str) -> None:
    """
    Enforces strong password policy:
    - Minimum 8 characters
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one number
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long."
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter."
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter."
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one digit."
        )


def hash_password(password: str) -> str:
    """Hashes a password with bcrypt and work factor salt."""
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash in constant time."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    subject: str,
    tier: str = "registered",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generates a cryptographically signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(subject),
        "tier": tier,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access"
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates JWT signature and claims."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "iat"]}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthSecurityError("Token has expired. Please log in again.")
    except (jwt.InvalidTokenError, getattr(jwt, "JWTError", Exception)):
        raise AuthSecurityError("Invalid authentication credentials.")


def get_token_claims(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """FastAPI dependency: requires valid bearer token, returns claims dict."""
    if not token:
        raise AuthSecurityError("Authentication credentials were not provided.")
    return decode_access_token(token)


def get_optional_token_claims(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """FastAPI dependency: extracts claims if token provided; returns None if anonymous."""
    if not token:
        return None
    try:
        return decode_access_token(token)
    except Exception:
        return None


def verify_resource_ownership(resource_owner_id: Optional[str], current_user_id: Optional[str], is_admin: bool = False) -> None:
    """
    Enforces object-level authorization:
    - Protects user-owned links and analytics from unauthorized access (IDOR prevention).
    - If resource belongs to a user, caller MUST be that user (or an admin).
    """
    if not resource_owner_id:
        # Anonymous resource
        return

    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to access this resource."
        )

    if resource_owner_id != current_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to view or manage this resource."
        )

