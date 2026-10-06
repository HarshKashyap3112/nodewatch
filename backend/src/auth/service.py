from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.config import auth_config
from src.auth.exceptions import InvalidCredentialsException, UserAlreadyExistsException, UserNotFoundException
from src.auth.models import User
from src.auth.schemas import RegisterIn, ResetPasswordIn, UserUpdateIn
from src.auth.utils import create_access_token, hash_password, verify_password


class AuthService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def register_user(db: AsyncSession, payload: RegisterIn) -> User:
        existing_user = await AuthService.get_user_by_email(db, payload.email)
        if existing_user:
            raise UserAlreadyExistsException()

        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            role=payload.role
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> str:
        user = await AuthService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role.value})
        return token

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, payload: UserUpdateIn) -> User:
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundException()

        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.password is not None:
            user.hashed_password = hash_password(payload.password)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def reset_password(db: AsyncSession, payload: ResetPasswordIn) -> User:
        if payload.reset_secret_key != auth_config.RESET_SECRET_KEY:
            raise InvalidCredentialsException(message="Invalid reset secret key")

        user = await AuthService.get_user_by_email(db, payload.email)
        if not user:
            raise UserNotFoundException(message="No account found with this email address")

        user.hashed_password = hash_password(payload.new_password)
        await db.commit()
        await db.refresh(user)
        return user

