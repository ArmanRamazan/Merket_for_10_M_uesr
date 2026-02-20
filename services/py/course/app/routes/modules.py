from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response

from app.domain.module import ModuleCreate, ModuleUpdate, ModuleResponse
from app.routes.courses import _get_current_user_claims
from app.services.module_service import ModuleService

router = APIRouter(tags=["modules"])


def _get_module_service() -> ModuleService:
    from app.main import get_module_service
    return get_module_service()


def _to_response(m: "Module") -> ModuleResponse:
    from app.domain.module import Module
    return ModuleResponse(
        id=m.id, course_id=m.course_id, title=m.title, order=m.order, created_at=m.created_at,
    )


@router.post("/courses/{course_id}/modules", response_model=ModuleResponse, status_code=201)
async def create_module(
    course_id: UUID,
    body: ModuleCreate,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[ModuleService, Depends(_get_module_service)],
) -> ModuleResponse:
    m = await service.create(
        course_id=course_id,
        teacher_id=claims["user_id"],
        role=claims["role"],
        is_verified=claims["is_verified"],
        title=body.title,
        order=body.order,
    )
    return _to_response(m)


@router.put("/modules/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: UUID,
    body: ModuleUpdate,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[ModuleService, Depends(_get_module_service)],
) -> ModuleResponse:
    fields = body.model_dump(exclude_none=True)
    m = await service.update(
        module_id=module_id,
        teacher_id=claims["user_id"],
        role=claims["role"],
        is_verified=claims["is_verified"],
        **fields,
    )
    return _to_response(m)


@router.delete("/modules/{module_id}", status_code=204)
async def delete_module(
    module_id: UUID,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[ModuleService, Depends(_get_module_service)],
) -> Response:
    await service.delete(
        module_id=module_id,
        teacher_id=claims["user_id"],
        role=claims["role"],
        is_verified=claims["is_verified"],
    )
    return Response(status_code=204)
