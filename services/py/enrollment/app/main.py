from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import asyncpg
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from common.database import create_pool
from common.errors import register_error_handlers
from app.config import Settings
from app.repositories.enrollment_repo import EnrollmentRepository
from app.services.enrollment_service import EnrollmentService
from app.routes.enrollments import router as enrollments_router

app_settings = Settings()

_pool: asyncpg.Pool | None = None
_enrollment_service: EnrollmentService | None = None


def get_enrollment_service() -> EnrollmentService:
    assert _enrollment_service is not None
    return _enrollment_service


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _pool, _enrollment_service

    _pool = await create_pool(app_settings.database_url)

    async with _pool.acquire() as conn:
        with open("migrations/001_enrollments.sql") as f:
            await conn.execute(f.read())

    repo = EnrollmentRepository(_pool)
    _enrollment_service = EnrollmentService(repo)
    yield
    await _pool.close()


app = FastAPI(title="Enrollment Service", lifespan=lifespan)
register_error_handlers(app)
app.include_router(enrollments_router)
Instrumentator().instrument(app).expose(app)
