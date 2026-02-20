# 05 — Infrastructure & Docker

> Последнее обновление: 2026-02-21
> Стадия: MVP (Phase 0)

---

## Docker Compose — два режима

### Dev (`docker-compose.dev.yml`)

```bash
docker compose -f docker-compose.dev.yml up
```

- Hot reload через volume mounts (`app/`, `migrations/`, `common/`)
- Debug ports для БД доступны с хоста
- Без мониторинга (нет Prometheus/Grafana)
- `--reload` флаг для uvicorn

**Сервисы:**
| Container | Image / Build | Порт |
|-----------|--------------|------|
| identity-db | postgres:16-alpine | 5433 |
| course-db | postgres:16-alpine | 5434 |
| enrollment-db | postgres:16-alpine | 5435 |
| payment-db | postgres:16-alpine | 5436 |
| notification-db | postgres:16-alpine | 5437 |
| redis | redis:7-alpine | 6379 |
| identity | Dockerfile build | 8001 |
| course | Dockerfile build | 8002 |
| enrollment | Dockerfile build | 8003 |
| payment | Dockerfile build | 8004 |
| notification | Dockerfile build | 8005 |
| seed (profile) | Dockerfile build | — |

### Prod (`docker-compose.prod.yml`)

```bash
docker compose -f docker-compose.prod.yml up -d
```

- Multi-worker uvicorn (4 workers)
- Prometheus + Grafana мониторинг
- Locust нагрузочное тестирование (profile)
- Без volume mounts (код запечён в image)

**Дополнительные сервисы:**
| Container | Image | Порт |
|-----------|-------|------|
| prometheus | prom/prometheus | 9090 |
| grafana | grafana/grafana | 3000 |
| locust (profile) | Dockerfile build | 8089 |

---

## Dockerfiles

Все Python Dockerfiles используют одинаковый паттерн:

```dockerfile
FROM python:3.12-slim

# uv binary (direct download, не COPY --from т.к. WSL2 credential issues)
ADD https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz /tmp/uv.tar.gz
RUN tar -xzf /tmp/uv.tar.gz -C /tmp \
    && mv /tmp/uv-x86_64-unknown-linux-gnu/uv /bin/uv \
    && rm -rf /tmp/uv*

WORKDIR /app

# Shared library
COPY libs/py/common /libs/common

# Dependencies install (layer cache)
COPY services/py/<service>/pyproject.toml .
RUN uv venv /app/.venv \
    && uv pip install --python /app/.venv /libs/common \
    && uv pip install --python /app/.venv <dependencies>

ENV PATH="/app/.venv/bin:$PATH"

# Application code
COPY services/py/<service>/ .

EXPOSE <port>
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "<port>"]
```

**Файлы:**
- `deploy/docker/identity.Dockerfile`
- `deploy/docker/course.Dockerfile`
- `deploy/docker/enrollment.Dockerfile`
- `deploy/docker/payment.Dockerfile`
- `deploy/docker/notification.Dockerfile`
- `deploy/docker/seed.Dockerfile`
- `deploy/docker/locust.Dockerfile`

---

## Environment Variables

### Общие (все Python сервисы)

| Variable | Default | Описание |
|----------|---------|----------|
| `DATABASE_URL` | — (required) | PostgreSQL DSN |
| `REDIS_URL` | `redis://localhost:6379` | Redis DSN (unused) |
| `JWT_SECRET` | `change-me-in-production` | Shared JWT secret |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_TTL_SECONDS` | `3600` | Token lifetime |

### Dev compose values

| Service | DATABASE_URL | JWT_SECRET |
|---------|-------------|------------|
| identity | `postgresql://identity:identity@identity-db:5432/identity` | `dev-secret-key` |
| course | `postgresql://course:course@course-db:5432/course` | `dev-secret-key` |
| enrollment | `postgresql://enrollment:enrollment@enrollment-db:5432/enrollment` | `dev-secret-key` |
| payment | `postgresql://payment:payment@payment-db:5432/payment` | `dev-secret-key` |
| notification | `postgresql://notification:notification@notification-db:5432/notification` | `dev-secret-key` |

### Seed-specific

| Variable | Value | Описание |
|----------|-------|----------|
| `IDENTITY_DB_URL` | `postgresql://identity:identity@identity-db:5432/identity` | Identity DB |
| `COURSE_DB_URL` | `postgresql://course:course@course-db:5432/course` | Course DB |
| `ENROLLMENT_DB_URL` | `postgresql://enrollment:enrollment@enrollment-db:5432/enrollment` | Enrollment DB |
| `PAYMENT_DB_URL` | `postgresql://payment:payment@payment-db:5432/payment` | Payment DB |
| `NOTIFICATION_DB_URL` | `postgresql://notification:notification@notification-db:5432/notification` | Notification DB |

---

## Seed Data

```bash
docker compose -f docker-compose.dev.yml --profile seed up seed
```

Скрипт `tools/seed/seed.py` генерирует:
- **1 admin** (`admin@eduplatform.com` / `password123`) — создаётся через INSERT перед bulk COPY
- **50,000 пользователей**: 80% students, 20% teachers (из них 70% verified)
- **100,000 курсов**: привязаны к verified teachers
- **~35,000 модулей**: 3-5 модулей на курс (первые 10K курсов)
- **~210,000 уроков**: 3-8 уроков на модуль (первые 10K курсов)
- **~100,000 отзывов**: рейтинг 1-5 (weighted: 40% пятёрок), обновляет avg_rating/review_count
- **200,000 записей (enrollments)**: 60% на бесплатные курсы, 40% на платные
- **50,000 оплат (payments)**: для платных курсов, status=completed
- Пароль для всех: `password123` (bcrypt hash)

---

## Monitoring (Prod only)

### Prometheus

Scrape config (`deploy/docker/prometheus/prometheus.yml`):
- `scrape_interval: 5s`
- Jobs: `identity` (`:8001`), `course` (`:8002`), `enrollment` (`:8003`), `payment` (`:8004`), `notification` (`:8005`)

Метрики автоматически экспортируются через `prometheus-fastapi-instrumentator`:
- `http_requests_total` — счётчик запросов
- `http_request_duration_seconds` — histogram latency
- `http_requests_in_progress` — gauge текущих запросов
- `http_response_size_bytes` — histogram размера ответов

### Grafana

- Datasource: Prometheus (auto-provisioned)
- Dashboard: `services.json` (auto-provisioned)
- Панели: Request Rate, Error Rate, P50/P95/P99 Latency, In-Progress, Response Size
- Refresh: 5s
- Default creds: admin/admin

---

## Load Testing (Prod only)

```bash
docker compose -f docker-compose.prod.yml --profile loadtest up locust
```

Locust UI: http://localhost:8089

**Сценарии** (`tools/locust/locustfile.py`):

| User Type | Weight | Действия |
|-----------|--------|----------|
| StudentUser | 7 | list_courses (5), view_course (3), view_curriculum (3), view_lesson (2), enroll_in_course (2), complete_lesson (1) |
| SearchUser | 2 | search_courses — ILIKE по random term |
| TeacherUser | 1 | get_me (2), create_course (1), list_my_courses (1) |

---

## Health Checks

| Container | Check | Interval | Timeout | Retries |
|-----------|-------|----------|---------|---------|
| identity-db | `pg_isready -U identity` | 5s | 3s | 5 |
| course-db | `pg_isready -U course` | 5s | 3s | 5 |
| enrollment-db | `pg_isready -U enrollment` | 5s | 3s | 5 |
| payment-db | `pg_isready -U payment` | 5s | 3s | 5 |
| notification-db | `pg_isready -U notification` | 5s | 3s | 5 |
| redis | `redis-cli ping` | 5s | 3s | 5 |

Все сервисы запускаются после `service_healthy` condition на своих БД.

---

## Frontend (вне Docker)

Buyer App запускается отдельно через npm:

```bash
cd apps/buyer && npm run dev  # :3001
```

Проксирует API через Next.js rewrites:
- `/api/identity/*` → `http://localhost:8001/*`
- `/api/course/*` → `http://localhost:8002/*`
- `/api/enrollment/*` → `http://localhost:8003/*`
- `/api/payment/*` → `http://localhost:8004/*`
- `/api/notification/*` → `http://localhost:8005/*`
