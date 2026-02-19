import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.product import Product
from app.repositories.product_repo import ProductRepository
from app.services.product_service import ProductService


@pytest.fixture
def seller_id():
    return uuid4()


@pytest.fixture
def product_id():
    return uuid4()


@pytest.fixture
def sample_product(product_id, seller_id):
    return Product(
        id=product_id,
        seller_id=seller_id,
        title="Test Product",
        description="A great product",
        price=Decimal("29.99"),
        stock=100,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=ProductRepository)


@pytest.fixture
def product_service(mock_repo):
    return ProductService(repo=mock_repo)
