from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])


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

