import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from common.errors import register_error_handlers, NotFoundError
from common.security import create_access_token
from app.domain.product import Product
from app.routes.products import router
from app.services.product_service import ProductService


@pytest.fixture
def mock_service():
    return AsyncMock(spec=ProductService)


@pytest.fixture
def test_app(mock_service):
    app = FastAPI()
    register_error_handlers(app)
    app.include_router(router)

    import app.main as main_module
    main_module.app_settings = type("S", (), {
        "jwt_secret": "test-secret",
        "jwt_algorithm": "HS256",
    })()
    main_module._product_service = mock_service

    return app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


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
def auth_token(seller_id):
    return create_access_token(str(seller_id), "test-secret")


@pytest.mark.asyncio
async def test_list_products(client, mock_service, sample_product):
    mock_service.list.return_value = ([sample_product], 1)

    resp = await client.get("/products")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == "Test Product"


@pytest.mark.asyncio
async def test_list_products_with_search(client, mock_service, sample_product):
    mock_service.search.return_value = ([sample_product], 1)

    resp = await client.get("/products?q=test")

    assert resp.status_code == 200
    mock_service.search.assert_called_once_with("test", 20, 0)


@pytest.mark.asyncio
async def test_list_products_with_pagination(client, mock_service):
    mock_service.list.return_value = ([], 0)

    resp = await client.get("/products?limit=10&offset=50")

    assert resp.status_code == 200
    mock_service.list.assert_called_once_with(10, 50)


@pytest.mark.asyncio
async def test_get_product(client, mock_service, sample_product):
    mock_service.get.return_value = sample_product

    resp = await client.get(f"/products/{sample_product.id}")

    assert resp.status_code == 200
    assert resp.json()["title"] == "Test Product"


@pytest.mark.asyncio
async def test_get_product_not_found(client, mock_service):
    mock_service.get.side_effect = NotFoundError("Product not found")

    resp = await client.get(f"/products/{uuid4()}")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_product(client, mock_service, sample_product, auth_token):
    mock_service.create.return_value = sample_product

    resp = await client.post(
        "/products",
        json={
            "title": "Test Product",
            "description": "A great product",
            "price": 29.99,
            "stock": 100,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert resp.status_code == 201
    assert resp.json()["title"] == "Test Product"
    mock_service.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_product_no_auth_returns_422(client):
    resp = await client.post("/products", json={
        "title": "Test",
        "description": "Desc",
        "price": 10.0,
        "stock": 5,
    })

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_product_invalid_token_returns_401(client):
    resp = await client.post(
        "/products",
        json={"title": "Test", "description": "Desc", "price": 10.0, "stock": 5},
        headers={"Authorization": "Bearer invalid"},
    )

    assert resp.status_code == 401
