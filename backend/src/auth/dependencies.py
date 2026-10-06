from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.constants import UserRole
from src.auth.exceptions import InvalidTokenException
from src.auth.models import User
from src.auth.service import AuthService
from src.auth.utils import decode_access_token
from src.database import get_db
from src.exceptions import ForbiddenException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise InvalidTokenException()

    user_id = payload["sub"]
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise InvalidTokenException()

    return user


def require_role(*roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenException("Operation not allowed for user role")
        return current_user

    return role_checker
