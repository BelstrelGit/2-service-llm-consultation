from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.repositories.users import UsersRepository
from app.usecases.auth import AuthUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_users_repo(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UsersRepository:
    return UsersRepository(session)


async def get_auth_uc(
    users_repo: Annotated[UsersRepository, Depends(get_users_repo)],
) -> AuthUseCase:
    return AuthUseCase(users_repo)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> int:
    try:
        payload = decode_token(token)
    except ValueError as e:
        error_msg = str(e).lower()
        if "expired" in error_msg:
            raise TokenExpiredError()
        raise InvalidTokenError()

    sub = payload.get("sub")
    if sub is None:
        raise InvalidTokenError()

    try:
        return int(sub)
    except (TypeError, ValueError):
        raise InvalidTokenError()
