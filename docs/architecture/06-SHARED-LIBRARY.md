# 06 — Shared Library (common)

> Последнее обновление: 2026-02-20
> Стадия: MVP (Phase 0)

---

## Расположение

```
libs/py/common/
├── pyproject.toml       # hatchling build, installable package
└── common/
    ├── __init__.py
    ├── config.py         # BaseAppSettings
    ├── database.py       # create_pool()
    ├── errors.py         # AppError hierarchy + register_error_handlers()
    └── security.py       # create_access_token(), decode_token()
```

**Установка:** `uv pip install /libs/common` или `common = { workspace = true }` в pyproject.toml сервиса.

---

## Модули

### `common.config`

```python
class BaseAppSettings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_ttl_seconds: int = 3600
```

Наследуется сервисами для добавления специфичных настроек. Все значения читаются из environment variables (pydantic-settings).

---

### `common.database`

```python
async def create_pool(dsn: str, min_size: int = 5, max_size: int = 5) -> asyncpg.Pool
```

Создаёт asyncpg connection pool. Pool size = 5 — намеренный bottleneck.

---

### `common.errors`

```python
class AppError(Exception):
    message: str
    status_code: int = 400

class NotFoundError(AppError):     # 404
class ForbiddenError(AppError):    # 403
class ConflictError(AppError):     # 409

def register_error_handlers(app: FastAPI) -> None
```

`register_error_handlers()` добавляет exception handler для `AppError`, который возвращает `{"detail": error.message}` с соответствующим HTTP status code.

---

### `common.security`

```python
def create_access_token(
    user_id: str,
    secret: str,
    algorithm: str = "HS256",
    ttl_seconds: int = 3600,
    extra_claims: dict | None = None,
) -> str

def decode_token(token: str, secret: str, algorithm: str = "HS256") -> dict
```

- `create_access_token()` — создаёт JWT с `sub`, `iat`, `exp` + optional extra_claims (role, is_verified)
- `decode_token()` — декодирует и валидирует JWT (проверяет expiration)

---

## Использование в сервисах

```python
# services/py/identity/app/config.py
from common.config import BaseAppSettings

class Settings(BaseAppSettings):
    jwt_ttl_seconds: int = 3600   # переопределение

# services/py/course/app/config.py
from common.config import BaseAppSettings

class Settings(BaseAppSettings):
    pass                           # всё из базового класса
```

---

## Правило выноса в common

Код выносится в `libs/py/common/` только когда используется в **2+ сервисах**. Все 4 модуля используются и в Identity, и в Course.
