import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from common.errors import NotFoundError
from app.domain.product import Product
from app.services.product_service import ProductService


@pytest.mark.asyncio
async def test_create_delegates_to_repo(product_service: ProductService, mock_repo: AsyncMock, sample_product: Product):
    mock_repo.create.return_value = sample_product

    result = await product_service.create(
        seller_id=sample_product.seller_id,
        title="Test Product",
        description="A great product",
        price=29.99,
        stock=100,
    )

    assert result.id == sample_product.id
    assert result.title == "Test Product"
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_success(product_service: ProductService, mock_repo: AsyncMock, sample_product: Product):
    mock_repo.get_by_id.return_value = sample_product

    result = await product_service.get(sample_product.id)

    assert result.id == sample_product.id
    mock_repo.get_by_id.assert_called_once_with(sample_product.id)


@pytest.mark.asyncio
async def test_get_not_found(product_service: ProductService, mock_repo: AsyncMock):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError, match="Product not found"):
        await product_service.get(uuid4())


@pytest.mark.asyncio
async def test_list_returns_items_and_total(product_service: ProductService, mock_repo: AsyncMock, sample_product: Product):
    mock_repo.list.return_value = ([sample_product], 1)

    items, total = await product_service.list(limit=20, offset=0)

    assert len(items) == 1
    assert total == 1
    assert items[0].id == sample_product.id


@pytest.mark.asyncio
async def test_search_delegates_to_repo(product_service: ProductService, mock_repo: AsyncMock, sample_product: Product):
    mock_repo.search.return_value = ([sample_product], 1)

    items, total = await product_service.search("test", limit=20, offset=0)

    assert len(items) == 1
    assert total == 1
    mock_repo.search.assert_called_once_with("test", 20, 0)
