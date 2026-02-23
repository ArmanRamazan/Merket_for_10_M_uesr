# EduPlatform — от 10K до 10M пользователей

Pet-проект: итеративное масштабирование учебной платформы. Начинаем с простого бэкенда на 10K пользователей и поэтапно оптимизируем архитектуру до 10M.

## Философия

Не строить «идеальную систему» на бумаге. Вместо этого:

1. **Запустить** — минимальный работающий бэкенд
2. **Нагрузить** — Locust, реальные сценарии, Grafana для метрик
3. **Найти bottleneck** — connection pool? full scan? GIL? отсутствие кэша?
4. **Оптимизировать** — точечно, с замерами до/после
5. **Повторить** — пока не выдержит целевую нагрузку

Каждый уровень масштаба (10K → 100K → 1M → 10M) — это переосмысление архитектуры на основе реальных данных, а не предположений.

## Текущий статус

**Стадия:** Phase 1.3 (UX & Product Quality) — 157 RPS, p99 51ms

| Компонент | Статус | Описание |
|-----------|--------|----------|
| Identity Service | ✅ Готов | Регистрация, логин, JWT refresh tokens, роли, admin, email verification, forgot password |
| Course Service | ✅ Готов | CRUD курсов, pg_trgm поиск, модули/уроки, отзывы, категории, фильтрация, XSS sanitization |
| Enrollment Service | ✅ Готов | Запись на курс, прогресс обучения, lesson completion, auto-completion |
| Payment Service | ✅ Готов | Mock-оплата, GET /me, GET /:id |
| Notification Service | ✅ Готов | In-app уведомления, mark as read |
| Buyer Frontend | ✅ Готов | Next.js 15 — каталог, поиск, уроки, прогресс, admin, TanStack Query, error boundaries |
| Shared Library | ✅ Готов | Config, errors, security, database, health checks, rate limiting |
| Docker Compose | ✅ Готов | Dev (hot reload) + Prod (monitoring, graceful shutdown) |
| Prometheus + Grafana | ✅ Готов | RPS, latency p50/p95/p99, error rate, pool metrics |
| Seed Script | ✅ Готов | 50K users + 100K courses + 200K enrollments + 100K reviews |
| Locust | ✅ Готов | 3 сценария: Student (70%), Search (20%), Teacher (10%) |
| Unit Tests | ✅ 157 тестов | identity 48, course 59, enrollment 25, payment 13, notification 12 |

## Стек

| Слой | Технология | Почему |
|------|-----------|--------|
| Бизнес-логика | Python 3.12 / FastAPI | Быстрая разработка, Clean Architecture |
| Performance-critical | Rust (будет) | API gateway, поиск, видео — когда Python упрётся в потолок |
| Frontend | Next.js 15 / Tailwind CSS 4 | SSR/SSG, App Router, TanStack Query |
| БД | PostgreSQL 16 | Каждый сервис — своя БД |
| Кэш / Rate limit | Redis 7 | Course cache (TTL 5min), rate limiting (sliding window), все сервисы |
| Метрики | Prometheus + Grafana | Автоматические метрики через prometheus-fastapi-instrumentator |
| Нагрузка | Locust | Сценарии, имитирующие реальный трафик |
| Пакеты | uv (Python), npm (JS) | uv workspace для монорепы |

## Быстрый старт

### Бэкенд (Docker)

```bash
# Dev — hot reload, volume mounts
docker compose -f docker-compose.dev.yml up

# Засеять данные (50K users + 100K courses)
docker compose -f docker-compose.dev.yml --profile seed up seed
```

### Фронтенд

```bash
cd apps/buyer
npm install
npm run dev    # http://localhost:3001
```

### Тесты

```bash
# Установить зависимости (из корня)
uv sync --all-packages

# Все 5 сервисов (157 тестов)
cd services/py/identity && uv run --package identity pytest tests/ -v
cd services/py/course && uv run --package course pytest tests/ -v
cd services/py/enrollment && uv run --package enrollment pytest tests/ -v
cd services/py/payment && uv run --package payment pytest tests/ -v
cd services/py/notification && uv run --package notification pytest tests/ -v
```

### Нагрузочное тестирование

```bash
# Prod stack + monitoring
docker compose -f docker-compose.prod.yml up -d

# Locust UI → http://localhost:8089
docker compose -f docker-compose.prod.yml --profile loadtest up locust

# Grafana → http://localhost:3000
```

## Порты

| Сервис | Порт |
|--------|------|
| Identity API | 8001 |
| Course API | 8002 |
| Enrollment API | 8003 |
| Payment API | 8004 |
| Notification API | 8005 |
| Buyer Frontend | 3001 |
| Grafana | 3000 |
| Prometheus | 9090 |
| Locust | 8089 |
| Identity DB (Postgres) | 5433 |
| Course DB (Postgres) | 5434 |
| Enrollment DB (Postgres) | 5435 |
| Payment DB (Postgres) | 5436 |
| Notification DB (Postgres) | 5437 |
| Redis | 6379 |

## Структура

```
├── libs/py/common/          — Shared: config, errors, security, database, health, rate limiting
├── services/py/identity/    — Auth: register, login, JWT refresh tokens, roles, admin, email verification, forgot password
├── services/py/course/      — Courses: CRUD, search, modules, lessons, reviews, categories, filtering, XSS sanitization
├── services/py/enrollment/  — Enrollment: запись на курс, прогресс, lesson completion, auto-completion
├── services/py/payment/     — Payment: mock-оплата
├── services/py/notification/— Notifications: in-app, mark as read
├── apps/buyer/              — Next.js frontend
├── deploy/docker/           — Dockerfiles, Prometheus, Grafana
├── tools/seed/              — Data generation (50K users, 100K courses, 200K enrollments)
├── tools/locust/            — Load test scenarios
├── docs/goals/              — Architecture decisions, domain specs
├── docs/architecture/       — Current system state (source of truth)
└── docs/phases/             — Implementation roadmap
```

## Roadmap

Подробный roadmap: [docs/goals/00-ROADMAP.md](docs/goals/00-ROADMAP.md)

| Стадия | Нагрузка | Ключевые изменения | Статус |
|--------|----------|-------------------|--------|
| **MVP** | 10K users | 5 Python сервисов, Next.js, Postgres, Locust | ✅ Готово |
| **Оптимизация** | 10K → 100K | Индексы, Redis кэш, rate limiting, refresh tokens, categories, email verification | 🟡 Phase 1.3 ✅ |
| **Масштабирование** | 100K → 1M | Rust gateway, Meilisearch, NATS events, read replicas | 🔴 Не начато |
| **Платформа** | 1M → 10M | Sharding, multi-region, video, live streaming | 🔴 Не начато |

## Документация

| Документ | Описание |
|----------|----------|
| [Видение продукта](docs/goals/01-PRODUCT-VISION.md) | Бизнес-метрики, user journeys, revenue |
| [Архитектура](docs/goals/02-ARCHITECTURE-PRINCIPLES.md) | ADR, принципы, выбор технологий |
| [Домены](docs/goals/04-DOMAINS.md) | Bounded contexts, event matrix |
| [Безопасность](docs/goals/06-SECURITY.md) | Threat model, mitigation |
| [Observability](docs/goals/09-OBSERVABILITY.md) | SLO, метрики, алерты |
| [Frontend](docs/goals/10-FRONTEND.md) | Next.js архитектура, performance budgets |
