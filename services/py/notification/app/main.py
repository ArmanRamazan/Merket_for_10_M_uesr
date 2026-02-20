from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import asyncpg
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from common.database import create_pool
from common.errors import register_error_handlers
from app.config import Settings
from app.repositories.notification_repo import NotificationRepository
from app.services.notification_service import NotificationService
from app.routes.notifications import router as notifications_router

app_settings = Settings()

_pool: asyncpg.Pool | None = None
_notification_service: NotificationService | None = None


def get_notification_service() -> NotificationService:
    assert _notification_service is not None
    return _notification_service


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _pool, _notification_service

    _pool = await create_pool(app_settings.database_url)

    async with _pool.acquire() as conn:
        with open("migrations/001_notifications.sql") as f:
            await conn.execute(f.read())

    repo = NotificationRepository(_pool)
    _notification_service = NotificationService(repo)
    yield
    await _pool.close()


app = FastAPI(title="Notification Service", lifespan=lifespan)
register_error_handlers(app)
app.include_router(notifications_router)
Instrumentator().instrument(app).expose(app)
