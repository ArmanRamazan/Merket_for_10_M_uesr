from __future__ import annotations

from uuid import UUID

import asyncpg

from common.errors import ConflictError, ForbiddenError
from app.domain.progress import LessonProgress
from app.repositories.progress_repo import ProgressRepository


class ProgressService:
    def __init__(self, repo: ProgressRepository) -> None:
        self._repo = repo

    async def complete_lesson(
        self, student_id: UUID, role: str, lesson_id: UUID, course_id: UUID
    ) -> LessonProgress:
        if role != "student":
            raise ForbiddenError("Only students can complete lessons")
        try:
            return await self._repo.complete_lesson(student_id, lesson_id, course_id)
        except asyncpg.UniqueViolationError as exc:
            raise ConflictError("Lesson already completed") from exc

    async def get_course_progress(
        self, student_id: UUID, course_id: UUID, total_lessons: int
    ) -> dict:
        completed = await self._repo.count_completed(student_id, course_id)
        percentage = (completed / total_lessons * 100) if total_lessons > 0 else 0.0
        return {
            "course_id": course_id,
            "completed_lessons": completed,
            "total_lessons": total_lessons,
            "percentage": round(percentage, 1),
        }

    async def list_completed_lessons(
        self, student_id: UUID, course_id: UUID
    ) -> list[UUID]:
        return await self._repo.list_completed_lessons(student_id, course_id)
