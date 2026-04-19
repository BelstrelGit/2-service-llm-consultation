from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_uc, get_current_user
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    data: RegisterRequest,
    uc: Annotated[AuthUseCase, Depends(get_auth_uc)],
):
    return await uc.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    uc: Annotated[AuthUseCase, Depends(get_auth_uc)],
):
    return await uc.login(email=form.username, password=form.password)


@router.get("/me", response_model=UserPublic)
async def me(
    user_id: Annotated[int, Depends(get_current_user)],
    uc: Annotated[AuthUseCase, Depends(get_auth_uc)],
):
    return await uc.me(user_id)
