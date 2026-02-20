from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response

from app.domain.lesson import LessonCreate, LessonUpdate, LessonResponse
from app.routes.courses import _get_current_user_claims
from app.services.lesson_service import LessonService

router = APIRouter(tags=["lessons"])


def _get_lesson_service() -> LessonService:
    from app.main import get_lesson_service
    return get_lesson_service()


def _to_response(l: "Lesson") -> LessonResponse:
    from app.domain.lesson import Lesson
    return LessonResponse(
        id=l.id,
        module_id=l.module_id,
        title=l.title,
        content=l.content,
        video_url=l.video_url,
        duration_minutes=l.duration_minutes,
        order=l.order,
        created_at=l.created_at,
    )


@router.post("/modules/{module_id}/lessons", response_model=LessonResponse, status_code=201)
async def create_lesson(
    module_id: UUID,
    body: LessonCreate,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[LessonService, Depends(_get_lesson_service)],
) -> LessonResponse:
    l = await service.create(
        module_id=module_id,
        teacher_id=claims["user_id"],
        role=claims["role"],
        is_verified=claims["is_verified"],
        title=body.title,
        content=body.content,
        video_url=body.video_url,
        duration_minutes=body.duration_minutes,
        order=body.order,
    )
    return _to_response(l)


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: UUID,
    service: Annotated[LessonService, Depends(_get_lesson_service)],
) -> LessonResponse:
    l = await service.get(lesson_id)
    return _to_response(l)


@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: UUID,
    body: LessonUpdate,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[LessonService, Depends(_get_lesson_service)],
) -> LessonResponse:
    fields = body.model_dump(exclude_none=True)
    l = await service.update(
        lesson_id=lesson_id,
        teacher_id=claims["user_id"],
        role=claims["role"],
        is_verified=claims["is_verified"],
        **fields,
    )
    return _to_response(l)


@router.delete("/lessons/{lesson_id}", status_code=204)
async def delete_lesson(
    lesson_id: UUID,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[LessonService, Depends(_get_lesson_service)],
) -> Response:
    await service.delete(
        lesson_id=lesson_id,
        teacher_id=claims["user_id"],
        role=claims["role"],
        is_verified=claims["is_verified"],
    )
    return Response(status_code=204)
