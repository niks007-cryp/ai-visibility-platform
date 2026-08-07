import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


class UserRepository:
    """Repository encapsulating database persistence operations for the User model."""

    async def create(
        self,
        db: AsyncSession,
        *,
        email: str,
        password_hash: str
    ) -> User:
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def get_by_id(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower().strip())
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


user_repository = UserRepository()
