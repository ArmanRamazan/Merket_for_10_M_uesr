from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import asyncpg
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from common.database import create_pool
from common.errors import register_error_handlers
from app.config import Settings
from app.repositories.product_repo import ProductRepository
from app.services.product_service import ProductService
from app.routes.products import router as products_router

app_settings = Settings()

_pool: asyncpg.Pool | None = None
_product_service: ProductService | None = None


def get_product_service() -> ProductService:
    assert _product_service is not None
    return _product_service


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _pool, _product_service

    _pool = await create_pool(app_settings.database_url)

    async with _pool.acquire() as conn:
        with open("migrations/001_products.sql") as f:
            await conn.execute(f.read())

    repo = ProductRepository(_pool)
    _product_service = ProductService(repo)
    yield
    await _pool.close()


app = FastAPI(title="Catalog Service", lifespan=lifespan)
register_error_handlers(app)
app.include_router(products_router)
Instrumentator().instrument(app).expose(app)
