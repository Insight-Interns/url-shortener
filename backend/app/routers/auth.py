import secrets
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth, OAuthError
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse,
)
from app.security.auth import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    get_token_claims,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

oauth = OAuth()
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
            "token_endpoint_auth_method": "client_secret_post",
        },
    )

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])


@router.get("/google/login", name="google_login", summary="Start Google sign-in")
async def google_login(request: Request):
    google = oauth.create_client("google")
    if google is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured on this server.",
        )
    return await google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)


@router.get("/google/callback", name="google_callback", summary="Complete Google sign-in")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    google = oauth.create_client("google")
    if google is None:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?oauth_error=not_configured")

    try:
        token = await google.authorize_access_token(request)
        profile = token.get("userinfo") or await google.userinfo(token=token)
    except OAuthError as exc:
        # Do not log the callback URL, authorization code, or token response.
        logger.warning("Google OAuth callback failed (%s): %s", exc.error, exc.description)
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?oauth_error=google_sign_in_failed")

    google_sub = profile.get("sub")
    email = str(profile.get("email") or "").strip().lower()
    if not google_sub or not email or profile.get("email_verified") is not True:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?oauth_error=unverified_google_account")

    user = db.query(User).filter(User.google_sub == google_sub).first()
    if user is None:
        user = db.query(User).filter(User.email == email).first()
        if user and user.google_sub and user.google_sub != google_sub:
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?oauth_error=account_already_linked")
        if user is None:
            # This password is random and never returned to the user; Google is the login method.
            user = User(
                email=email,
                hashed_password=hash_password(secrets.token_urlsafe(48)),
                full_name=profile.get("name"),
                tier="registered",
                is_active=True,
                google_sub=google_sub,
            )
            db.add(user)
        else:
            user.google_sub = google_sub

        try:
            db.commit()
            db.refresh(user)
        except Exception as exc:
            db.rollback()
            logger.error("Google account provisioning failed (%s)", type(exc).__name__)
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?oauth_error=account_setup_failed")

    if not user.is_active:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?oauth_error=account_disabled")

    app_token = create_access_token(subject=user.id, tier=user.tier)
    # Put the app token in the URL fragment: browsers do not send fragments to the server.
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback#access_token={app_token}")


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user:
    1. Validates email format and password strength.
    2. Ensures unique email address.
    3. Hashes password with bcrypt.
    4. Issues a signed JWT access token.
    """
    validate_password_strength(payload.password)

    # Check for existing email
    existing_user = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists."
        )

    # Securely hash password
    hashed_pwd = hash_password(payload.password)

    new_user = User(
        email=payload.email.lower(),
        hashed_password=hashed_pwd,
        full_name=payload.full_name,
        tier="registered",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Issue JWT
    token = create_access_token(subject=new_user.id, tier=new_user.tier)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfileResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            tier=new_user.tier,
            created_at=new_user.created_at
        )
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain JWT access token"
)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user credentials and issues a signed JWT access token.
    """
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        # Generic error message to prevent account enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact support."
        )

    token = create_access_token(subject=user.id, tier=user.tier)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            tier=user.tier,
            created_at=user.created_at
        )
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Retrieve current authenticated user profile"
)
def get_current_user_profile(
    claims: dict = Depends(get_token_claims),
    db: Session = Depends(get_db)
):
    """
    Retrieves the authenticated user's profile from verified JWT claims.
    """
    user_id = claims.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        tier=user.tier,
        created_at=user.created_at
    )

