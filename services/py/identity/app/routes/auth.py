from typing import Annotated
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, Header

from common.errors import AppError
from app.domain.user import UserCreate, UserLogin, TokenPair, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


def _get_auth_service() -> AuthService:
    from app.main import get_auth_service
    return get_auth_service()


def _get_current_user_id(authorization: Annotated[str, Header()]) -> UUID:
    from app.main import app_settings

    if not authorization.startswith("Bearer "):
        raise AppError("Invalid authorization header", status_code=401)
    token = authorization[7:]
    try:
        payload = jwt.decode(
            token, app_settings.jwt_secret, algorithms=[app_settings.jwt_algorithm]
        )
        return UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise AppError("Invalid token", status_code=401) from exc


@router.post("/register", response_model=TokenPair)
async def register(
    body: UserCreate,
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> TokenPair:
    return await service.register(body.email, body.password, body.name)


@router.post("/login", response_model=TokenPair)
async def login(
    body: UserLogin,
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> TokenPair:
    return await service.authenticate(body.email, body.password)


@router.get("/me", response_model=UserResponse)
async def me(
    user_id: Annotated[UUID, Depends(_get_current_user_id)],
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> UserResponse:
    user = await service.get_by_id(user_id)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
    )
