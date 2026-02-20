import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from common.errors import ForbiddenError, NotFoundError
from app.domain.course import Course
from app.domain.module import Module
from app.domain.lesson import Lesson
from app.services.lesson_service import LessonService


@pytest.mark.asyncio
async def test_create_lesson(lesson_service: LessonService, mock_lesson_repo: AsyncMock, mock_module_repo: AsyncMock, mock_repo: AsyncMock, sample_course: Course, sample_module: Module, sample_lesson: Lesson, teacher_id):
    mock_module_repo.get_by_id.return_value = sample_module
    mock_repo.get_by_id.return_value = sample_course
    mock_lesson_repo.create.return_value = sample_lesson

    result = await lesson_service.create(
        module_id=sample_module.id, teacher_id=teacher_id,
        role="teacher", is_verified=True,
        title="Первый урок", content="Содержимое", video_url=None,
        duration_minutes=30, order=0,
    )

    assert result.id == sample_lesson.id


@pytest.mark.asyncio
async def test_get_lesson(lesson_service: LessonService, mock_lesson_repo: AsyncMock, sample_lesson: Lesson):
    mock_lesson_repo.get_by_id.return_value = sample_lesson

    result = await lesson_service.get(sample_lesson.id)

    assert result.title == "Первый урок"


@pytest.mark.asyncio
async def test_update_lesson(lesson_service: LessonService, mock_lesson_repo: AsyncMock, mock_module_repo: AsyncMock, mock_repo: AsyncMock, sample_course: Course, sample_module: Module, sample_lesson: Lesson, teacher_id):
    mock_lesson_repo.get_by_id.return_value = sample_lesson
    mock_module_repo.get_by_id.return_value = sample_module
    mock_repo.get_by_id.return_value = sample_course
    mock_lesson_repo.update.return_value = sample_lesson

    result = await lesson_service.update(
        lesson_id=sample_lesson.id, teacher_id=teacher_id,
        role="teacher", is_verified=True, title="Обновлённый урок",
    )

    assert result.id == sample_lesson.id


@pytest.mark.asyncio
async def test_delete_lesson(lesson_service: LessonService, mock_lesson_repo: AsyncMock, mock_module_repo: AsyncMock, mock_repo: AsyncMock, sample_course: Course, sample_module: Module, sample_lesson: Lesson, teacher_id):
    mock_lesson_repo.get_by_id.return_value = sample_lesson
    mock_module_repo.get_by_id.return_value = sample_module
    mock_repo.get_by_id.return_value = sample_course
    mock_lesson_repo.delete.return_value = True

    await lesson_service.delete(
        lesson_id=sample_lesson.id, teacher_id=teacher_id,
        role="teacher", is_verified=True,
    )

    mock_lesson_repo.delete.assert_called_once_with(sample_lesson.id)


@pytest.mark.asyncio
async def test_create_lesson_forbidden_student(lesson_service: LessonService):
    with pytest.raises(ForbiddenError, match="Only verified teachers"):
        await lesson_service.create(
            module_id=uuid4(), teacher_id=uuid4(),
            role="student", is_verified=False,
            title="Test", content="", video_url=None,
            duration_minutes=0, order=0,
        )
