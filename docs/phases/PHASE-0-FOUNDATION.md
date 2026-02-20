# Phase 0 — Foundation (MVP на 10K пользователей)

> **Цель:** запустить работающую учебную платформу с полным циклом обучения. Студент может найти курс, записаться, пройти уроки, увидеть прогресс, оставить отзыв. Преподаватель может создать курс с уроками и видеть студентов.
>
> **Намеренные ограничения:** нет кэша, нет индексов на поиск, маленький connection pool. Это не баги — это будущие точки оптимизации.

---

## Milestone 0.1 — Инфраструктура и shared libs ✅

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

## Milestone 0.2 — Backend сервисы ✅

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

## Milestone 0.3 — Frontend ✅

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

## Milestone 0.5 — Enrollment + Payment + Notification ✅

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
| 0.5.10 | Architecture docs обновлены (01-06) | ✅ Done |

---

## Milestone 0.6 — Lessons + Progress + Reviews ✅

> **Цель:** замкнуть цикл обучения. Без этого платформа — каталог пустых карточек.

### 0.6.1 — Контент курса (модули + уроки)

| # | Задача | Статус |
|---|--------|--------|
| 0.6.1.1 | SQL: таблицы `modules` и `lessons` в course-db | ✅ Done |
| 0.6.1.2 | Domain: Module, Lesson dataclasses | ✅ Done |
| 0.6.1.3 | Repository: CRUD modules + lessons | ✅ Done |
| 0.6.1.4 | Service: create/update/delete modules + lessons (teacher only, owner check) | ✅ Done |
| 0.6.1.5 | Routes: POST/PUT/DELETE /courses/:id/modules, POST/PUT/DELETE /modules/:id/lessons | ✅ Done |
| 0.6.1.6 | GET /courses/:id/curriculum — программа курса (modules + lessons, без content) | ✅ Done |
| 0.6.1.7 | GET /lessons/:id — полное содержимое урока (markdown + video_url) | ✅ Done |
| 0.6.1.8 | Unit тесты | ✅ Done |

### 0.6.2 — Прогресс студента

| # | Задача | Статус |
|---|--------|--------|
| 0.6.2.1 | SQL: таблица `lesson_progress` в enrollment-db | ✅ Done |
| 0.6.2.2 | POST /progress/lessons/:id/complete — отметить урок пройденным | ✅ Done |
| 0.6.2.3 | GET /progress/courses/:id — прогресс (completed / total lessons) | ✅ Done |
| 0.6.2.4 | Автоматический enrollment.status = completed при 100% | ⏳ Deferred to 0.7 |
| 0.6.2.5 | Unit тесты | ✅ Done |

### 0.6.3 — Teacher tools (базовые)

| # | Задача | Статус |
|---|--------|--------|
| 0.6.3.1 | GET /courses/my — курсы текущего teacher | ✅ Done |
| 0.6.3.2 | PUT /courses/:id — редактирование курса (owner check) | ✅ Done |
| 0.6.3.3 | Unit тесты | ✅ Done |

### 0.6.4 — Reviews & Ratings

| # | Задача | Статус |
|---|--------|--------|
| 0.6.4.1 | SQL: таблица `reviews` (новый сервис или course-db) | ✅ Done |
| 0.6.4.2 | POST /reviews — оценка курса (1-5 + текст, только enrolled students) | ✅ Done |
| 0.6.4.3 | GET /reviews/course/:id — отзывы курса | ✅ Done |
| 0.6.4.4 | Денормализация: avg_rating + review_count в courses | ✅ Done |
| 0.6.4.5 | Unit тесты | ✅ Done |

### 0.6.5 — Frontend

| # | Задача | Статус |
|---|--------|--------|
| 0.6.5.1 | Страница курса: программа (модули + уроки) | ✅ Done |
| 0.6.5.2 | Страница урока: markdown render + video embed + кнопка "Завершить" | ✅ Done |
| 0.6.5.3 | Прогресс-бар на странице курса | ✅ Done |
| 0.6.5.4 | Teacher: страница "Мои курсы" + кнопка "Добавить модуль/урок" | ✅ Done |
| 0.6.5.5 | Форма отзыва + список отзывов + средний рейтинг на карточке | ✅ Done |

### 0.6.6 — Seed + Locust + Docs

| # | Задача | Статус |
|---|--------|--------|
| 0.6.6.1 | Seed: 3-5 модулей × 5-10 уроков на курс | ✅ Done |
| 0.6.6.2 | Seed: lesson_progress для enrolled students | ✅ Done |
| 0.6.6.3 | Seed: reviews + ratings | ✅ Done |
| 0.6.6.4 | Locust: LessonUser (проходит уроки) | ✅ Done |
| 0.6.6.5 | Architecture docs обновлены | ✅ Done |

### 0.6.7 — Admin Role + Teacher Verification + UX Fixes

| # | Задача | Статус |
|---|--------|--------|
| 0.6.7.1 | Migration 003: admin value в ENUM user_role | ✅ Done |
| 0.6.7.2 | Domain: UserRole.ADMIN, PendingTeacherResponse | ✅ Done |
| 0.6.7.3 | Repository: list_unverified_teachers(), set_verified() | ✅ Done |
| 0.6.7.4 | Service: list_pending_teachers(), verify_teacher() (admin only) | ✅ Done |
| 0.6.7.5 | Routes: GET /admin/teachers/pending, PATCH /admin/users/{id}/verify | ✅ Done |
| 0.6.7.6 | Tests: 7 service + 5 route = 12 new (32 total identity) | ✅ Done |
| 0.6.7.7 | Frontend: admin panel (/admin/teachers), Header admin link | ✅ Done |
| 0.6.7.8 | Teacher UX: redirect to edit, inline lesson editing, confirm delete, verification banner | ✅ Done |
| 0.6.7.9 | Student UX: enrollment feedback, mobile sidebar toggle, breadcrumbs, course completion | ✅ Done |
| 0.6.7.10 | Seed: admin user (admin@eduplatform.com / password123) | ✅ Done |
| 0.6.7.11 | Architecture docs обновлены | ✅ Done |

---

## Milestone 0.7 — Baseline и первые bottleneck-и 🔴 ← ТЕКУЩИЙ

| # | Задача | Статус |
|---|--------|--------|
| 0.7.1 | Поднять prod stack (docker-compose.prod.yml) | ✅ Done |
| 0.7.2 | Засеять полные данные | ✅ Done |
| 0.7.3 | Запустить Locust: 100 users, ramp 10/s, 5 минут | ✅ Done |
| 0.7.4 | Зафиксировать baseline в Grafana (screenshots) | ✅ Done |
| 0.7.5 | Найти первый bottleneck | ✅ Done |

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

**Course Service** теперь также содержит modules + lessons (в той же course-db).
**Enrollment Service** теперь также содержит lesson_progress (в той же enrollment-db).

**Learning flow (клиент-оркестратор):**
```
Бесплатный:  Student → POST /enrollments → 201
Платный:     Student → POST /payments → POST /enrollments → POST /notifications

Обучение:    Student → GET /courses/:id/curriculum → список модулей/уроков
             Student → GET /lessons/:id → содержимое урока
             Student → POST /progress/lessons/:id/complete → отметка
             Student → GET /progress/courses/:id → 85% done

Отзыв:      Student → POST /reviews → {rating: 5, comment: "..."}
```

---

## Ожидаемые bottleneck-и

| При нагрузке | Что сломается | Как увидим | Как починим |
|-------------|---------------|-----------|-------------|
| ~50 RPS search | ILIKE full scan на 100K rows | p99 > 500ms в Grafana | pg_trgm + GIN index |
| ~100 RPS curriculum | JOIN modules + lessons per course | p99 > 300ms | Denormalization / Redis |
| ~200 RPS | asyncpg pool = 5 connections | 503 errors spike | Pool 20 + PgBouncer |
| ~500 RPS | Каждый запрос идёт в БД | DB CPU > 80% | Redis кэш |
| ~1000 RPS | Python GIL, 1 worker | CPU 100% на 1 core | uvicorn --workers 4 |

---

## Критерии завершения Phase 0

- [x] Студент может зарегистрироваться, найти курс, посмотреть карточку
- [x] Преподаватель (verified) может создать курс
- [x] Студент НЕ может создать курс (403)
- [x] Студент может записаться на курс (бесплатный и платный)
- [x] Пять сервисов с отдельными БД
- [x] Unit тесты проходят (113 тестов: identity 32, course 40, enrollment 20, payment 11, notification 10)
- [x] Мониторинг (Prometheus + Grafana) настроен
- [x] Locust сценарии готовы
- [x] **Студент может пройти курс: уроки → прогресс → completion**
- [x] **Преподаватель может добавить уроки в курс**
- [x] **Курс имеет рейтинг и отзывы**
- [ ] Baseline метрики зафиксированы
- [ ] Первый bottleneck найден и задокументирован
