import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.auth_exception import ForbiddenError, InvalidTokenError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
import uuid


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise InvalidTokenError("Missing Authorization Header.")
    try:
        payload = decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")

    if payload.get("type") != "access":
        raise InvalidTokenError("Expected an access token")

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        raise InvalidTokenError("Malformed token subject")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise InvalidTokenError("User no longer exists")

    return user


def require_role(role: str):

    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != role:
            raise ForbiddenError(f"This action requires the '{role}' role")
        return current_user

    return _check
