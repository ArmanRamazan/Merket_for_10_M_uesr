from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import asyncpg
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from common.database import create_pool, update_pool_metrics
from common.errors import register_error_handlers
from app.config import Settings
from app.repositories.payment_repo import PaymentRepository
from app.services.payment_service import PaymentService
from app.routes.payments import router as payments_router

app_settings = Settings()

_pool: asyncpg.Pool | None = None
_payment_service: PaymentService | None = None


def get_payment_service() -> PaymentService:
    assert _payment_service is not None
    return _payment_service


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _pool, _payment_service

    _pool = await create_pool(app_settings.database_url)

    async with _pool.acquire() as conn:
        with open("migrations/001_payments.sql") as f:
            await conn.execute(f.read())

    repo = PaymentRepository(_pool)
    _payment_service = PaymentService(repo)
    yield
    await _pool.close()


app = FastAPI(title="Payment Service", lifespan=lifespan)
register_error_handlers(app)
app.include_router(payments_router)


@app.middleware("http")
async def pool_metrics_middleware(request, call_next):  # type: ignore[no-untyped-def]
    if _pool is not None:
        update_pool_metrics(_pool, "payment")
    return await call_next(request)


Instrumentator().instrument(app).expose(app)
