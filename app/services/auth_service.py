import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import TokenResponse
from app.repositories.user_repository import user_repository, UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_jwt

logger = logging.getLogger("app.service.auth")


class AuthService:
    """Service layer managing user authentication, registration, password hashing, and token issuance."""

    def __init__(self, user_repo: UserRepository = user_repository):
        self.user_repo = user_repo

    async def register_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> User:
        """Registers a new platform user with unique email check and hashed password."""
        existing = await self.user_repo.get_by_email(db, email=email)
        if existing:
            logger.warning("event=register_failed reason=email_already_exists email=%s", email)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email address already exists."
            )

        pwd_hash = hash_password(password)
        user = await self.user_repo.create(db, email=email, password_hash=pwd_hash)
        logger.info("event=user_registered user_id=%s email=%s", user.id, email)
        return user

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> TokenResponse:
        """Authenticates user credentials and returns JWT Access & Refresh token pair."""
        user = await self.user_repo.get_by_email(db, email=email)
        if not user or not verify_password(password, user.password_hash):
            logger.warning("event=login_failed reason=invalid_credentials email=%s", email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password credentials."
            )

        access_token = create_access_token(user_id=user.id, email=user.email)
        refresh_token = create_refresh_token(user_id=user.id)

        logger.info("event=user_authenticated user_id=%s", user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_token(
        self,
        db: AsyncSession,
        refresh_token_str: str
    ) -> TokenResponse:
        """Decodes refresh token and issues fresh JWT access/refresh token pair."""
        payload = decode_jwt(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            logger.warning("event=token_refresh_failed reason=invalid_token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token."
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

        user = await self.user_repo.get_by_id(db, user_id=uuid.UUID(user_id_str))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

        access_token = create_access_token(user_id=user.id, email=user.email)
        new_refresh_token = create_refresh_token(user_id=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )


auth_service = AuthService()
