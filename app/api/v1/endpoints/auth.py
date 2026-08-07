from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth_deps import get_current_user
from app.core.rate_limiter import rate_limiter
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest
from app.services.auth_service import auth_service, AuthService

router = APIRouter()


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New Platform User",
    description="Registers a new user account with unique email validation and hashed password."
)
async def register(
    request: Request,
    payload: UserRegister,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(lambda: auth_service)
) -> UserResponse:
    rate_limiter.check_rate_limit(request, key_prefix="auth_register", max_requests=5, window_seconds=60)
    return await service.register_user(db, email=payload.email, password=payload.password)


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate User & Issue Tokens",
    description="Authenticates credentials and issues signed JWT Access and Refresh token pair."
)
async def login(
    request: Request,
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(lambda: auth_service)
) -> TokenResponse:
    rate_limiter.check_rate_limit(request, key_prefix="auth_login", max_requests=5, window_seconds=60)
    return await service.authenticate_user(db, email=payload.email, password=payload.password)


@router.post(
    "/auth/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh JWT Tokens",
    description="Exchanges valid Refresh Token for fresh Access and Refresh tokens."
)
async def refresh_tokens(
    request: Request,
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    service: AuthService = Depends(lambda: auth_service)
) -> TokenResponse:
    rate_limiter.check_rate_limit(request, key_prefix="auth_refresh", max_requests=10, window_seconds=60)
    return await service.refresh_token(db, refresh_token_str=payload.refresh_token)


@router.post(
    "/auth/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout User Session",
    description="Invalidates current user session."
)
async def logout(
    current_user: User = Depends(get_current_user)
):
    return {"message": f"User '{current_user.email}' successfully logged out."}


@router.get(
    "/auth/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Returns profile details of current authenticated user."
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return current_user
