from __future__ import annotations

from uuid import UUID

import asyncpg

from common.errors import ConflictError, ForbiddenError
from app.domain.enrollment import Enrollment
from app.repositories.enrollment_repo import EnrollmentRepository


class EnrollmentService:
    def __init__(self, repo: EnrollmentRepository) -> None:
        self._repo = repo

    async def enroll(
        self,
        student_id: UUID,
        role: str,
        course_id: UUID,
        payment_id: UUID | None,
    ) -> Enrollment:
        if role != "student":
            raise ForbiddenError("Only students can enroll in courses")

        try:
            return await self._repo.create(student_id, course_id, payment_id)
        except asyncpg.UniqueViolationError as exc:
            raise ConflictError("Already enrolled in this course") from exc

    async def list_my(
        self, student_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[Enrollment], int]:
        return await self._repo.list_by_student(student_id, limit, offset)

    async def count_by_course(self, course_id: UUID) -> int:
        return await self._repo.count_by_course(course_id)
