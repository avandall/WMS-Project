"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.api.schemas.auth import LoginRequest, TokenResponse, UserCreate, RefreshRequest, UserResponse
from app.repositories.sql.user_repo import UserRepo
from app.services.user_service import UserService
from app.core.database import get_session
from app.core.auth import decode_token, create_token
from app.core.settings import settings

router = APIRouter()
bearer = HTTPBearer(auto_error=False)


def get_user_service(db=Depends(get_session)) -> UserService:
    return UserService(UserRepo(db))


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate, service: UserService = Depends(get_user_service)):
    user = service.create_user(email=payload.email, password=payload.password, role=payload.role, full_name=payload.full_name)
    return UserResponse.from_domain(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, service: UserService = Depends(get_user_service)):
    tokens = service.authenticate(payload.email, payload.password)
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        user=UserResponse.from_domain(tokens["user"]),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, service: UserService = Depends(get_user_service)):
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = service.get_user(int(decoded.get("sub")))
    access = create_token(
        str(user.user_id),
        settings.access_token_expire_minutes,
        {"role": user.role},
    )
    refresh_token = create_token(str(user.user_id), settings.refresh_token_expire_minutes, {"role": user.role, "type": "refresh"})
    return TokenResponse(
        access_token=access,
        refresh_token=refresh_token,
        user=UserResponse.from_domain(user),
    )
