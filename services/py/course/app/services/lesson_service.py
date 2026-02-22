from __future__ import annotations

from uuid import UUID

from common.errors import ForbiddenError, NotFoundError
from app.cache import CourseCache
from app.domain.lesson import Lesson
from app.domain.module import Module
from app.repositories.course_repo import CourseRepository
from app.repositories.module_repo import ModuleRepository
from app.repositories.lesson_repo import LessonRepository


class LessonService:
    def __init__(
        self,
        repo: LessonRepository,
        module_repo: ModuleRepository,
        course_repo: CourseRepository,
        cache: CourseCache | None = None,
    ) -> None:
        self._repo = repo
        self._module_repo = module_repo
        self._course_repo = course_repo
        self._cache = cache

    async def _check_owner_via_module(self, module_id: UUID, teacher_id: UUID) -> Module:
        module = await self._module_repo.get_by_id(module_id)
        if not module:
            raise NotFoundError("Module not found")
        course = await self._course_repo.get_by_id(module.course_id)
        if not course:
            raise NotFoundError("Course not found")
        if course.teacher_id != teacher_id:
            raise ForbiddenError("Only the course owner can manage lessons")
        return module

    async def create(
        self,
        module_id: UUID,
        teacher_id: UUID,
        role: str,
        is_verified: bool,
        title: str,
        content: str,
        video_url: str | None,
        duration_minutes: int,
        order: int,
    ) -> Lesson:
        if role != "teacher" or not is_verified:
            raise ForbiddenError("Only verified teachers can manage lessons")
        module = await self._check_owner_via_module(module_id, teacher_id)
        lesson = await self._repo.create(module_id, title, content, video_url, duration_minutes, order)
        if self._cache:
            await self._cache.invalidate_course(module.course_id)
        return lesson

    async def get(self, lesson_id: UUID) -> Lesson:
        lesson = await self._repo.get_by_id(lesson_id)
        if not lesson:
            raise NotFoundError("Lesson not found")
        return lesson

    async def update(
        self, lesson_id: UUID, teacher_id: UUID, role: str, is_verified: bool, **fields: object
    ) -> Lesson:
        if role != "teacher" or not is_verified:
            raise ForbiddenError("Only verified teachers can manage lessons")
        lesson = await self._repo.get_by_id(lesson_id)
        if not lesson:
            raise NotFoundError("Lesson not found")
        module = await self._check_owner_via_module(lesson.module_id, teacher_id)
        updated = await self._repo.update(lesson_id, **fields)
        if not updated:
            raise NotFoundError("Lesson not found")
        if self._cache:
            await self._cache.invalidate_course(module.course_id)
        return updated

    async def delete(
        self, lesson_id: UUID, teacher_id: UUID, role: str, is_verified: bool
    ) -> None:
        if role != "teacher" or not is_verified:
            raise ForbiddenError("Only verified teachers can manage lessons")
        lesson = await self._repo.get_by_id(lesson_id)
        if not lesson:
            raise NotFoundError("Lesson not found")
        module = await self._check_owner_via_module(lesson.module_id, teacher_id)
        await self._repo.delete(lesson_id)
        if self._cache:
            await self._cache.invalidate_course(module.course_id)
