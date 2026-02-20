import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from common.errors import ForbiddenError, NotFoundError
from app.domain.course import Course
from app.domain.module import Module
from app.services.module_service import ModuleService


@pytest.mark.asyncio
async def test_create_module(module_service: ModuleService, mock_module_repo: AsyncMock, mock_repo: AsyncMock, sample_course: Course, sample_module: Module, teacher_id):
    mock_repo.get_by_id.return_value = sample_course
    mock_module_repo.create.return_value = sample_module

    result = await module_service.create(
        course_id=sample_course.id, teacher_id=teacher_id,
        role="teacher", is_verified=True, title="Введение", order=0,
    )

    assert result.id == sample_module.id
    mock_module_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_list_modules(module_service: ModuleService, mock_module_repo: AsyncMock, sample_module: Module, course_id):
    mock_module_repo.list_by_course.return_value = [sample_module]

    result = await module_service.list_by_course(course_id)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_update_module(module_service: ModuleService, mock_module_repo: AsyncMock, mock_repo: AsyncMock, sample_course: Course, sample_module: Module, teacher_id):
    mock_module_repo.get_by_id.return_value = sample_module
    mock_repo.get_by_id.return_value = sample_course
    mock_module_repo.update.return_value = sample_module

    result = await module_service.update(
        module_id=sample_module.id, teacher_id=teacher_id,
        role="teacher", is_verified=True, title="Новое название",
    )

    assert result.id == sample_module.id


@pytest.mark.asyncio
async def test_delete_module(module_service: ModuleService, mock_module_repo: AsyncMock, mock_repo: AsyncMock, sample_course: Course, sample_module: Module, teacher_id):
    mock_module_repo.get_by_id.return_value = sample_module
    mock_repo.get_by_id.return_value = sample_course
    mock_module_repo.delete.return_value = True

    await module_service.delete(
        module_id=sample_module.id, teacher_id=teacher_id,
        role="teacher", is_verified=True,
    )

    mock_module_repo.delete.assert_called_once_with(sample_module.id)


@pytest.mark.asyncio
async def test_create_module_forbidden_not_owner(module_service: ModuleService, mock_repo: AsyncMock, sample_course: Course, course_id):
    mock_repo.get_by_id.return_value = sample_course

    with pytest.raises(ForbiddenError, match="Only the course owner"):
        await module_service.create(
            course_id=course_id, teacher_id=uuid4(),
            role="teacher", is_verified=True, title="Test", order=0,
        )
