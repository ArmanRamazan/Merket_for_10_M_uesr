from __future__ import annotations

from uuid import UUID

from common.errors import ForbiddenError, NotFoundError
from app.domain.module import Module
from app.repositories.course_repo import CourseRepository
from app.repositories.module_repo import ModuleRepository


class ModuleService:
    def __init__(self, repo: ModuleRepository, course_repo: CourseRepository) -> None:
        self._repo = repo
        self._course_repo = course_repo

    async def _check_owner(self, course_id: UUID, teacher_id: UUID) -> None:
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")
        if course.teacher_id != teacher_id:
            raise ForbiddenError("Only the course owner can manage modules")

    async def create(
        self, course_id: UUID, teacher_id: UUID, role: str, is_verified: bool, title: str, order: int
    ) -> Module:
        if role != "teacher" or not is_verified:
            raise ForbiddenError("Only verified teachers can manage modules")
        await self._check_owner(course_id, teacher_id)
        return await self._repo.create(course_id, title, order)

    async def list_by_course(self, course_id: UUID) -> list[Module]:
        return await self._repo.list_by_course(course_id)

    async def update(
        self, module_id: UUID, teacher_id: UUID, role: str, is_verified: bool, **fields: object
    ) -> Module:
        if role != "teacher" or not is_verified:
            raise ForbiddenError("Only verified teachers can manage modules")
        module = await self._repo.get_by_id(module_id)
        if not module:
            raise NotFoundError("Module not found")
        await self._check_owner(module.course_id, teacher_id)
        updated = await self._repo.update(module_id, **fields)
        if not updated:
            raise NotFoundError("Module not found")
        return updated

    async def delete(self, module_id: UUID, teacher_id: UUID, role: str, is_verified: bool) -> None:
        if role != "teacher" or not is_verified:
            raise ForbiddenError("Only verified teachers can manage modules")
        module = await self._repo.get_by_id(module_id)
        if not module:
            raise NotFoundError("Module not found")
        await self._check_owner(module.course_id, teacher_id)
        await self._repo.delete(module_id)
