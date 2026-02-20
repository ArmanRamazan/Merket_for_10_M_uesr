import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

import asyncpg

from common.errors import ConflictError, ForbiddenError
from app.domain.progress import LessonProgress
from app.services.progress_service import ProgressService


@pytest.mark.asyncio
async def test_complete_lesson(progress_service: ProgressService, mock_progress_repo: AsyncMock, sample_progress: LessonProgress, student_id, lesson_id, course_id):
    mock_progress_repo.complete_lesson.return_value = sample_progress

    result = await progress_service.complete_lesson(
        student_id=student_id, role="student",
        lesson_id=lesson_id, course_id=course_id,
    )

    assert result.lesson_id == lesson_id
    mock_progress_repo.complete_lesson.assert_called_once()


@pytest.mark.asyncio
async def test_complete_lesson_duplicate(progress_service: ProgressService, mock_progress_repo: AsyncMock, student_id, lesson_id, course_id):
    mock_progress_repo.complete_lesson.side_effect = asyncpg.UniqueViolationError("")

    with pytest.raises(ConflictError, match="already completed"):
        await progress_service.complete_lesson(
            student_id=student_id, role="student",
            lesson_id=lesson_id, course_id=course_id,
        )


@pytest.mark.asyncio
async def test_complete_lesson_teacher_forbidden(progress_service: ProgressService):
    with pytest.raises(ForbiddenError, match="Only students"):
        await progress_service.complete_lesson(
            student_id=uuid4(), role="teacher",
            lesson_id=uuid4(), course_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_get_course_progress(progress_service: ProgressService, mock_progress_repo: AsyncMock, student_id, course_id):
    mock_progress_repo.count_completed.return_value = 3

    result = await progress_service.get_course_progress(
        student_id=student_id, course_id=course_id, total_lessons=10,
    )

    assert result["completed_lessons"] == 3
    assert result["total_lessons"] == 10
    assert result["percentage"] == 30.0


@pytest.mark.asyncio
async def test_list_completed_lessons(progress_service: ProgressService, mock_progress_repo: AsyncMock, student_id, course_id, lesson_id):
    mock_progress_repo.list_completed_lessons.return_value = [lesson_id]

    result = await progress_service.list_completed_lessons(student_id, course_id)

    assert len(result) == 1
    assert result[0] == lesson_id
