"""Authentication routes."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_db, get_current_active_user
from app.db.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserCreate, UserResponse, Token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)

    if await repo.get_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await repo.get_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role="researcher",
    )
    return await repo.create(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled")

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return Token(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/demo-login", response_model=Token)
async def demo_login(db: AsyncSession = Depends(get_db)):
    """Demo login for hackathon showcase — creates demo user if not exists."""
    repo = UserRepository(db)
    user = await repo.get_by_username("demo")

    if not user:
        user = User(
            email="demo@climatetwin.in",
            username="demo",
            hashed_password=get_password_hash("demo123"),
            full_name="Demo Researcher",
            role="researcher",
        )
        user = await repo.create(user)

    token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )
