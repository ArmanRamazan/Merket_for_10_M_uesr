from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import asyncpg
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from common.database import create_pool
from common.errors import register_error_handlers
from app.config import Settings
from app.repositories.course_repo import CourseRepository
from app.services.course_service import CourseService
from app.routes.courses import router as courses_router

app_settings = Settings()

_pool: asyncpg.Pool | None = None
_course_service: CourseService | None = None


def get_course_service() -> CourseService:
    assert _course_service is not None
    return _course_service


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _pool, _course_service

    _pool = await create_pool(app_settings.database_url)

    async with _pool.acquire() as conn:
        with open("migrations/001_courses.sql") as f:
            await conn.execute(f.read())

    repo = CourseRepository(_pool)
    _course_service = CourseService(repo)
    yield
    await _pool.close()


app = FastAPI(title="Course Service", lifespan=lifespan)
register_error_handlers(app)
app.include_router(courses_router)
Instrumentator().instrument(app).expose(app)
