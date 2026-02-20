from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.domain.progress import LessonCompleteRequest, CourseProgressResponse
from app.routes.enrollments import _get_current_user_claims
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/progress", tags=["progress"])


def _get_progress_service() -> ProgressService:
    from app.main import get_progress_service
    return get_progress_service()


@router.post("/lessons/{lesson_id}/complete", status_code=201)
async def complete_lesson(
    lesson_id: UUID,
    body: LessonCompleteRequest,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[ProgressService, Depends(_get_progress_service)],
) -> dict:
    progress = await service.complete_lesson(
        student_id=claims["user_id"],
        role=claims["role"],
        lesson_id=lesson_id,
        course_id=body.course_id,
    )
    return {
        "id": progress.id,
        "lesson_id": progress.lesson_id,
        "course_id": progress.course_id,
        "completed_at": progress.completed_at.isoformat(),
    }


@router.get("/courses/{course_id}", response_model=CourseProgressResponse)
async def get_course_progress(
    course_id: UUID,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[ProgressService, Depends(_get_progress_service)],
    total_lessons: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    return await service.get_course_progress(
        student_id=claims["user_id"],
        course_id=course_id,
        total_lessons=total_lessons,
    )


@router.get("/courses/{course_id}/lessons")
async def list_completed_lessons(
    course_id: UUID,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[ProgressService, Depends(_get_progress_service)],
) -> dict:
    lesson_ids = await service.list_completed_lessons(
        student_id=claims["user_id"],
        course_id=course_id,
    )
    return {"course_id": course_id, "completed_lesson_ids": lesson_ids}
