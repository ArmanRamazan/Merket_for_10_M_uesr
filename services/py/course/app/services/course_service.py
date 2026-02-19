from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from common.errors import ForbiddenError, NotFoundError
from app.domain.course import Course, CourseLevel
from app.repositories.course_repo import CourseRepository


class CourseService:
    def __init__(self, repo: CourseRepository) -> None:
        self._repo = repo

    async def create(
        self,
        teacher_id: UUID,
        role: str,
        is_verified: bool,
        title: str,
        description: str,
        is_free: bool,
        price: Decimal | None,
        duration_minutes: int,
        level: CourseLevel,
    ) -> Course:
        if role != "teacher":
            raise ForbiddenError("Only teachers can create courses")
        if not is_verified:
            raise ForbiddenError("Only verified teachers can create courses")
        return await self._repo.create(
            teacher_id, title, description, is_free, price, duration_minutes, level
        )

    async def get(self, course_id: UUID) -> Course:
        course = await self._repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")
        return course

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Course], int]:
        return await self._repo.list(limit, offset)

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> tuple[list[Course], int]:
        return await self._repo.search(query, limit, offset)
