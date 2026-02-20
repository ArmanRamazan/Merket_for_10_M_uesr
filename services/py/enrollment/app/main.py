from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import asyncpg
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from common.database import create_pool, update_pool_metrics
from common.errors import register_error_handlers
from app.config import Settings
from app.repositories.enrollment_repo import EnrollmentRepository
from app.repositories.progress_repo import ProgressRepository
from app.services.enrollment_service import EnrollmentService
from app.services.progress_service import ProgressService
from app.routes.enrollments import router as enrollments_router
from app.routes.progress import router as progress_router

app_settings = Settings()

_pool: asyncpg.Pool | None = None
_enrollment_service: EnrollmentService | None = None
_progress_service: ProgressService | None = None


def get_enrollment_service() -> EnrollmentService:
    assert _enrollment_service is not None
    return _enrollment_service


def get_progress_service() -> ProgressService:
    assert _progress_service is not None
    return _progress_service


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _pool, _enrollment_service, _progress_service

    _pool = await create_pool(app_settings.database_url)

    async with _pool.acquire() as conn:
        with open("migrations/001_enrollments.sql") as f:
            await conn.execute(f.read())
        with open("migrations/002_lesson_progress.sql") as f:
            await conn.execute(f.read())

    enrollment_repo = EnrollmentRepository(_pool)
    progress_repo = ProgressRepository(_pool)
    _enrollment_service = EnrollmentService(enrollment_repo)
    _progress_service = ProgressService(progress_repo)
    yield
    await _pool.close()


app = FastAPI(title="Enrollment Service", lifespan=lifespan)
register_error_handlers(app)
app.include_router(enrollments_router)
app.include_router(progress_router)


@app.middleware("http")
async def pool_metrics_middleware(request, call_next):  # type: ignore[no-untyped-def]
    if _pool is not None:
        update_pool_metrics(_pool, "enrollment")
    return await call_next(request)


Instrumentator().instrument(app).expose(app)
