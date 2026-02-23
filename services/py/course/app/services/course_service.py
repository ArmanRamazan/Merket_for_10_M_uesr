from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from common.errors import ForbiddenError, NotFoundError
from app.cache import CourseCache
from app.sanitize import sanitize_text, sanitize_html
from app.domain.course import Course, CourseLevel, CourseResponse, CurriculumModule, CurriculumResponse
from app.domain.lesson import LessonResponse
from app.repositories.course_repo import CourseRepository
from app.repositories.module_repo import ModuleRepository
from app.repositories.lesson_repo import LessonRepository


class CourseService:
    def __init__(
        self,
        repo: CourseRepository,
        module_repo: ModuleRepository | None = None,
        lesson_repo: LessonRepository | None = None,
        cache: CourseCache | None = None,
    ) -> None:
        self._repo = repo
        self._module_repo = module_repo
        self._lesson_repo = lesson_repo
        self._cache = cache

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
        title = sanitize_text(title)
        description = sanitize_html(description)
        return await self._repo.create(
            teacher_id, title, description, is_free, price, duration_minutes, level
        )

    async def get(self, course_id: UUID) -> Course:
        if self._cache:
            cached = await self._cache.get_course(course_id)
            if cached:
                return Course(
                    id=UUID(cached["id"]),
                    teacher_id=UUID(cached["teacher_id"]),
                    title=cached["title"],
                    description=cached["description"],
                    is_free=cached["is_free"],
                    price=Decimal(cached["price"]) if cached["price"] is not None else None,
                    duration_minutes=cached["duration_minutes"],
                    level=CourseLevel(cached["level"]),
                    created_at=cached["created_at"],
                    avg_rating=Decimal(cached["avg_rating"]) if cached.get("avg_rating") is not None else None,
                    review_count=cached.get("review_count", 0),
                )

        course = await self._repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")

        if self._cache:
            await self._cache.set_course(course_id, {
                "id": str(course.id),
                "teacher_id": str(course.teacher_id),
                "title": course.title,
                "description": course.description,
                "is_free": course.is_free,
                "price": str(course.price) if course.price is not None else None,
                "duration_minutes": course.duration_minutes,
                "level": course.level.value,
                "created_at": course.created_at.isoformat(),
                "avg_rating": str(course.avg_rating) if course.avg_rating is not None else None,
                "review_count": course.review_count,
            })

        return course

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Course], int]:
        return await self._repo.list(limit, offset)

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> tuple[list[Course], int]:
        return await self._repo.search(query, limit, offset)

    async def list_my(
        self, teacher_id: UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[Course], int]:
        return await self._repo.list_by_teacher(teacher_id, limit, offset)

    async def list_cursor(
        self, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[Course], int, str | None]:
        return await self._repo.list_cursor(limit, cursor)

    async def search_cursor(
        self, query: str, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[Course], int, str | None]:
        return await self._repo.search_cursor(query, limit, cursor)

    async def list_my_cursor(
        self, teacher_id: UUID, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[Course], int, str | None]:
        return await self._repo.list_by_teacher_cursor(teacher_id, limit, cursor)

    async def update(
        self,
        course_id: UUID,
        teacher_id: UUID,
        role: str,
        is_verified: bool,
        **fields: object,
    ) -> Course:
        if role != "teacher" or not is_verified:
            raise ForbiddenError("Only verified teachers can update courses")
        course = await self._repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")
        if course.teacher_id != teacher_id:
            raise ForbiddenError("Only the course owner can update this course")
        if "title" in fields and isinstance(fields["title"], str):
            fields["title"] = sanitize_text(fields["title"])
        if "description" in fields and isinstance(fields["description"], str):
            fields["description"] = sanitize_html(fields["description"])
        updated = await self._repo.update(course_id, **fields)
        if not updated:
            raise NotFoundError("Course not found")
        if self._cache:
            await self._cache.invalidate_course(course_id)
        return updated

    async def get_curriculum(self, course_id: UUID) -> CurriculumResponse:
        if self._cache:
            cached = await self._cache.get_curriculum(course_id)
            if cached:
                return CurriculumResponse(**cached)

        course = await self._repo.get_by_id(course_id)
        if not course:
            raise NotFoundError("Course not found")

        assert self._module_repo is not None
        assert self._lesson_repo is not None

        modules = await self._module_repo.list_by_course(course_id)
        total_lessons = 0
        curriculum_modules: list[CurriculumModule] = []

        for m in modules:
            lessons = await self._lesson_repo.list_by_module(m.id)
            total_lessons += len(lessons)
            curriculum_modules.append(
                CurriculumModule(
                    id=m.id,
                    course_id=m.course_id,
                    title=m.title,
                    order=m.order,
                    created_at=m.created_at,
                    lessons=[
                        LessonResponse(
                            id=l.id,
                            module_id=l.module_id,
                            title=l.title,
                            content=l.content,
                            video_url=l.video_url,
                            duration_minutes=l.duration_minutes,
                            order=l.order,
                            created_at=l.created_at,
                        )
                        for l in lessons
                    ],
                )
            )

        course_resp = CourseResponse(
            id=course.id,
            teacher_id=course.teacher_id,
            title=course.title,
            description=course.description,
            is_free=course.is_free,
            price=course.price,
            duration_minutes=course.duration_minutes,
            level=course.level,
            created_at=course.created_at,
            avg_rating=course.avg_rating,
            review_count=course.review_count,
        )

        result = CurriculumResponse(
            course=course_resp,
            modules=curriculum_modules,
            total_lessons=total_lessons,
        )

        if self._cache:
            await self._cache.set_curriculum(course_id, result.model_dump(mode="json"))

        return result
