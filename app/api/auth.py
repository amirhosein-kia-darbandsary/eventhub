
from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.schemas.auth import TokenResponse, RegisterRequest, LoginRequest
from fastapi import status
from app.core.security import create_access_token, create_refresh_token, verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password
from app.exceptions.auth_exception import InvalidCredentialsError

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post('/register', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name
    )
    db.add(user)
    await db.commit()
    await db.flush(user)

    return TokenResponse(access_token=create_access_token(subject=user.id,
                                                          role=user.role),
                         refresh_token=create_refresh_token(subject=user.id,
                                                            role=user.role))
    
@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise InvalidCredentialsError()

    return TokenResponse(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id), user.role.value),
    )
