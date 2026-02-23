from typing import Annotated
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, Header, Query

from common.errors import AppError
from app.domain.user import PendingTeacherResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/admin", tags=["admin"])


def _get_auth_service() -> AuthService:
    from app.main import get_auth_service
    return get_auth_service()


def _get_current_user_claims(authorization: Annotated[str, Header()]) -> dict:
    from app.main import app_settings

    if not authorization.startswith("Bearer "):
        raise AppError("Invalid authorization header", status_code=401)
    token = authorization[7:]
    try:
        payload = jwt.decode(
            token, app_settings.jwt_secret, algorithms=[app_settings.jwt_algorithm]
        )
        return {"sub": UUID(payload["sub"]), "role": payload.get("role", "student")}
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise AppError("Invalid token", status_code=401) from exc


@router.get("/teachers/pending")
async def list_pending_teachers(
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[AuthService, Depends(_get_auth_service)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    teachers, total = await service.list_pending_teachers(claims["role"], limit, offset)
    return {
        "items": [
            PendingTeacherResponse(
                id=t.id, email=t.email, name=t.name, created_at=t.created_at
            )
            for t in teachers
        ],
        "total": total,
    }


@router.patch("/users/{user_id}/verify", response_model=UserResponse)
async def verify_teacher(
    user_id: UUID,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[AuthService, Depends(_get_auth_service)],
) -> UserResponse:
    user = await service.verify_teacher(claims["role"], user_id)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        email_verified=user.email_verified,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )
