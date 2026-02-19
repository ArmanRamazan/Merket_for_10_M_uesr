import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from common.errors import ForbiddenError, NotFoundError
from app.domain.course import Course, CourseLevel
from app.services.course_service import CourseService


@pytest.mark.asyncio
async def test_create_course_by_verified_teacher(course_service: CourseService, mock_repo: AsyncMock, sample_course: Course, teacher_id):
    mock_repo.create.return_value = sample_course

    result = await course_service.create(
        teacher_id=teacher_id,
        role="teacher",
        is_verified=True,
        title="Python для начинающих",
        description="Базовый курс по Python",
        is_free=True,
        price=None,
        duration_minutes=120,
        level=CourseLevel.BEGINNER,
    )

    assert result.id == sample_course.id
    assert result.title == "Python для начинающих"
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_course_forbidden_for_student(course_service: CourseService):
    with pytest.raises(ForbiddenError, match="Only teachers can create courses"):
        await course_service.create(
            teacher_id=uuid4(),
            role="student",
            is_verified=False,
            title="Test",
            description="",
            is_free=True,
            price=None,
            duration_minutes=0,
            level=CourseLevel.BEGINNER,
        )


@pytest.mark.asyncio
async def test_create_course_forbidden_for_unverified_teacher(course_service: CourseService):
    with pytest.raises(ForbiddenError, match="Only verified teachers can create courses"):
        await course_service.create(
            teacher_id=uuid4(),
            role="teacher",
            is_verified=False,
            title="Test",
            description="",
            is_free=True,
            price=None,
            duration_minutes=0,
            level=CourseLevel.BEGINNER,
        )


@pytest.mark.asyncio
async def test_get_course_success(course_service: CourseService, mock_repo: AsyncMock, sample_course: Course):
    mock_repo.get_by_id.return_value = sample_course

    result = await course_service.get(sample_course.id)

    assert result.id == sample_course.id
    mock_repo.get_by_id.assert_called_once_with(sample_course.id)


@pytest.mark.asyncio
async def test_get_course_not_found(course_service: CourseService, mock_repo: AsyncMock):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError, match="Course not found"):
        await course_service.get(uuid4())


@pytest.mark.asyncio
async def test_list_courses(course_service: CourseService, mock_repo: AsyncMock, sample_course: Course):
    mock_repo.list.return_value = ([sample_course], 1)

    items, total = await course_service.list(limit=20, offset=0)

    assert len(items) == 1
    assert total == 1
    mock_repo.list.assert_called_once_with(20, 0)


@pytest.mark.asyncio
async def test_search_courses(course_service: CourseService, mock_repo: AsyncMock, sample_course: Course):
    mock_repo.search.return_value = ([sample_course], 1)

    items, total = await course_service.search("python", limit=20, offset=0)

    assert len(items) == 1
    mock_repo.search.assert_called_once_with("python", 20, 0)
