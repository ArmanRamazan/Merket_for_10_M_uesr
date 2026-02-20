# Phase 0 — Foundation (MVP на 10K пользователей)

> **Цель:** запустить работающую учебную платформу. Identity + Course + Frontend. Нагрузить Locust-ом, увидеть первые bottleneck-и, зафиксировать baseline.
>
> **Намеренные ограничения:** нет кэша, нет индексов на поиск, маленький connection pool. Это не баги — это будущие точки оптимизации.

---

## Milestone 0.1 — Инфраструктура и shared libs

| # | Задача | Статус |
|---|--------|--------|
| 0.1.1 | uv workspace (Python монорепа) | ✅ Done |
| 0.1.2 | Shared library: config (BaseSettings), errors (ForbiddenError), security (JWT + extra_claims), database (asyncpg pool) | ✅ Done |
| 0.1.3 | Docker Compose dev: hot reload, volume mounts | ✅ Done |
| 0.1.4 | Docker Compose prod: multi-worker, restart policies, env vars | ✅ Done |
| 0.1.5 | Prometheus + Grafana: auto-provision, dashboard (RPS, latency p50/p95/p99, errors) | ✅ Done |
| 0.1.6 | Seed script: 50K users (students + teachers) + 100K courses (asyncpg COPY) | ✅ Done |
| 0.1.7 | Locust: StudentUser (70%), SearchUser (20%), TeacherUser (10%) | ✅ Done |

---

## Milestone 0.2 — Backend сервисы

| # | Задача | Статус |
|---|--------|--------|
| 0.2.1 | **Identity Service** — POST /register (с role), POST /login, GET /me (role + is_verified) | ✅ Done |
| 0.2.2 | **Course Service** — GET /courses (list + ILIKE search), GET /courses/:id, POST /courses (role-based access) | ✅ Done |
| 0.2.3 | Database-per-service: identity-db (port 5433), course-db (port 5434) | ✅ Done |
| 0.2.4 | SQL миграции при старте (CREATE TABLE IF NOT EXISTS, ENUM types) | ✅ Done |
| 0.2.5 | JWT shared secret — role и is_verified в claims, оба сервиса валидируют токен сами | ✅ Done |
| 0.2.6 | prometheus-fastapi-instrumentator — автоматические метрики | ✅ Done |
| 0.2.7 | Unit тесты: identity + course | ✅ Done |

---

## Milestone 0.3 — Frontend

| # | Задача | Статус |
|---|--------|--------|
| 0.3.1 | Next.js 15 buyer app (Tailwind CSS 4, TypeScript strict) | ✅ Done |
| 0.3.2 | Каталог курсов с поиском | ✅ Done |
| 0.3.3 | Детали курса (уровень, цена, длительность) | ✅ Done |
| 0.3.4 | Регистрация с выбором роли (студент/преподаватель) / Логин (JWT в localStorage) | ✅ Done |
| 0.3.5 | Создание курса (только для verified teachers) | ✅ Done |
| 0.3.6 | API proxy через Next.js rewrites | ✅ Done |
| 0.3.7 | Role badge в Header | ✅ Done |

---

## Milestone 0.4 — Baseline и первые bottleneck-и

| # | Задача | Статус |
|---|--------|--------|
| 0.4.1 | Поднять prod stack (docker-compose.prod.yml) | 🔴 Not Started |
| 0.4.2 | Засеять 50K users + 100K courses | 🔴 Not Started |
| 0.4.3 | Запустить Locust: 100 users, ramp 10/s, 5 минут | 🔴 Not Started |
| 0.4.4 | Зафиксировать baseline в Grafana (screenshots) | 🔴 Not Started |
| 0.4.5 | Найти первый bottleneck (ожидание: ILIKE search) | 🔴 Not Started |

---

## Milestone 0.5 — Enrollment + Payment + Notification

| # | Задача | Статус |
|---|--------|--------|
| 0.5.1 | **Enrollment Service** (:8003) — POST /enrollments (student only), GET /me, GET /course/:id/count | ✅ Done |
| 0.5.2 | **Payment Service** (:8004) — POST /payments (mock, always completed), GET /:id, GET /me | ✅ Done |
| 0.5.3 | **Notification Service** (:8005) — POST (log to stdout), GET /me, PATCH /:id/read | ✅ Done |
| 0.5.4 | Docker: 3 Dockerfiles + compose dev/prod + 3 новых DB (5435-5437) | ✅ Done |
| 0.5.5 | Prometheus: 3 новых jobs, Grafana: regex обновлён | ✅ Done |
| 0.5.6 | Frontend: enrollment кнопка, "Мои курсы", "Уведомления" pages, Header links | ✅ Done |
| 0.5.7 | Seed: +200K enrollments + 50K payments | ✅ Done |
| 0.5.8 | Locust: StudentUser enroll task (payment → enrollment) | ✅ Done |
| 0.5.9 | Unit тесты: enrollment (12) + payment (11) + notification (10) | ✅ Done |
| 0.5.10 | Architecture docs обновлены (01-05) | ✅ Done |

---

## Архитектура MVP

```
                         ┌────────────┐
                         │   Buyer    │
                         │  Next.js   │
                         │   :3001    │
                         └─────┬──────┘
                               │ /api proxy
        ┌──────────┬───────────┼───────────┬──────────┐
        │          │           │           │          │
   ┌────▼───┐ ┌───▼────┐ ┌───▼─────┐ ┌───▼───┐ ┌───▼──────┐
   │Identity│ │ Course │ │Enrollm. │ │Payment│ │Notificat.│
   │ :8001  │ │ :8002  │ │ :8003   │ │ :8004 │ │  :8005   │
   └───┬────┘ └───┬────┘ └───┬─────┘ └───┬───┘ └───┬──────┘
       │          │           │           │         │
  ┌────▼───┐ ┌───▼────┐ ┌───▼─────┐ ┌───▼───┐ ┌───▼──────┐
  │identity│ │course  │ │enroll-  │ │payment│ │notificat.│
  │  db    │ │  db    │ │ment db │ │  db   │ │  db      │
  │ :5433  │ │ :5434  │ │ :5435  │ │ :5436 │ │  :5437   │
  └────────┘ └────────┘ └────────┘ └───────┘ └──────────┘
```

**Enrollment flow (клиент-оркестратор):**
```
Бесплатный:  Student → POST /enrollments → 201

Платный:     Student → POST /payments → 201
             Student → POST /enrollments {payment_id} → 201
             Student → POST /notifications → 201
```

## Ожидаемые bottleneck-и

| При нагрузке | Что сломается | Как увидим | Как починим |
|-------------|---------------|-----------|-------------|
| ~50 RPS search | ILIKE full scan на 100K rows | p99 > 500ms в Grafana | pg_trgm + GIN index |
| ~200 RPS | asyncpg pool = 5 connections | 503 errors spike | Pool 20 + PgBouncer |
| ~500 RPS | Каждый запрос идёт в БД | DB CPU > 80% | Redis кэш (course list, get by id) |
| ~1000 RPS | Python GIL, 1 worker | CPU 100% на 1 core | uvicorn --workers 4 |

## Критерии завершения Phase 0

- [x] Студент может зарегистрироваться, найти курс, посмотреть карточку
- [x] Преподаватель (verified) может создать курс
- [x] Студент НЕ может создать курс (403)
- [x] Студент может записаться на курс (бесплатный и платный)
- [x] Пять сервисов с отдельными БД
- [x] Unit тесты проходят
- [x] Мониторинг (Prometheus + Grafana) настроен
- [x] Locust сценарии готовы
- [ ] Baseline метрики зафиксированы
- [ ] Первый bottleneck найден и задокументирован
