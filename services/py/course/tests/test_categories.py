import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.category import Category
from app.repositories.category_repo import CategoryRepository


@pytest.fixture
def mock_category_repo():
    return AsyncMock(spec=CategoryRepository)


@pytest.fixture
def sample_categories():
    return [
        Category(id=uuid4(), name="Programming", slug="programming"),
        Category(id=uuid4(), name="Design", slug="design"),
        Category(id=uuid4(), name="Business", slug="business"),
    ]


@pytest.mark.asyncio
async def test_list_all_categories(mock_category_repo, sample_categories):
    mock_category_repo.list_all.return_value = sample_categories
    result = await mock_category_repo.list_all()
    assert len(result) == 3
    assert result[0].name == "Programming"
    assert result[0].slug == "programming"


@pytest.mark.asyncio
async def test_get_category_by_id(mock_category_repo, sample_categories):
    cat = sample_categories[0]
    mock_category_repo.get_by_id.return_value = cat
    result = await mock_category_repo.get_by_id(cat.id)
    assert result is not None
    assert result.id == cat.id
    assert result.name == "Programming"


@pytest.mark.asyncio
async def test_get_category_not_found(mock_category_repo):
    mock_category_repo.get_by_id.return_value = None
    result = await mock_category_repo.get_by_id(uuid4())
    assert result is None


async def test_create_course_with_category(
    course_service, mock_repo, teacher_id, sample_categories
):
    from app.domain.course import Course, CourseLevel
    from datetime import datetime, timezone

    cat_id = sample_categories[0].id
    course = Course(
        id=uuid4(),
        teacher_id=teacher_id,
        title="Python Basics",
        description="Learn Python",
        is_free=True,
        price=None,
        duration_minutes=60,
        level=CourseLevel.BEGINNER,
        created_at=datetime.now(timezone.utc),
        category_id=cat_id,
    )
    mock_repo.create.return_value = course

    result = await course_service.create(
        teacher_id=teacher_id,
        role="teacher",
        is_verified=True,
        title="Python Basics",
        description="Learn Python",
        is_free=True,
        price=None,
        duration_minutes=60,
        level=CourseLevel.BEGINNER,
        category_id=cat_id,
    )
    assert result.category_id == cat_id


async def test_list_filtered_by_category(course_service, mock_repo, sample_course):
    mock_repo.list_filtered.return_value = ([sample_course], 1)
    items, total = await course_service.list_filtered(category_id=uuid4())
    assert total == 1
    mock_repo.list_filtered.assert_called_once()


async def test_list_filtered_by_level(course_service, mock_repo, sample_course):
    mock_repo.list_filtered.return_value = ([sample_course], 1)
    items, total = await course_service.list_filtered(level="beginner")
    assert total == 1


async def test_list_filtered_by_is_free(course_service, mock_repo, sample_course):
    mock_repo.list_filtered.return_value = ([sample_course], 1)
    items, total = await course_service.list_filtered(is_free=True)
    assert total == 1


async def test_list_filtered_with_sort(course_service, mock_repo, sample_course):
    mock_repo.list_filtered.return_value = ([sample_course], 1)
    items, total = await course_service.list_filtered(sort_by="avg_rating")
    assert total == 1
    call_kwargs = mock_repo.list_filtered.call_args[1]
    assert call_kwargs["sort_by"] == "avg_rating"
