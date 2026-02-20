from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import asyncpg
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from common.database import create_pool
from common.errors import register_error_handlers
from app.config import Settings
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router

app_settings = Settings()

_pool: asyncpg.Pool | None = None
_auth_service: AuthService | None = None


def get_auth_service() -> AuthService:
    assert _auth_service is not None
    return _auth_service


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _pool, _auth_service

    _pool = await create_pool(app_settings.database_url)

    async with _pool.acquire() as conn:
        with open("migrations/001_users.sql") as f:
            await conn.execute(f.read())
        with open("migrations/002_add_role.sql") as f:
            await conn.execute(f.read())
        with open("migrations/003_add_admin_role.sql") as f:
            await conn.execute(f.read())

    repo = UserRepository(_pool)
    _auth_service = AuthService(
        repo=repo,
        jwt_secret=app_settings.jwt_secret,
        jwt_algorithm=app_settings.jwt_algorithm,
        jwt_ttl_seconds=app_settings.jwt_ttl_seconds,
    )
    yield
    await _pool.close()


app = FastAPI(title="Identity Service", lifespan=lifespan)
register_error_handlers(app)
app.include_router(auth_router)
app.include_router(admin_router)
Instrumentator().instrument(app).expose(app)
