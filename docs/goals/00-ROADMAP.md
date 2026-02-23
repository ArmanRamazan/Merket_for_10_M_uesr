# EduPlatform — Roadmap

> **Подход:** итеративное масштабирование. Запустить → нагрузить → найти bottleneck → оптимизировать → повторить.
>
> Каждая стадия — не «теоретическое проектирование», а реальная работа с метриками. Переход к следующей стадии только когда текущая держит целевую нагрузку.

---

## Стадии масштабирования

```
MVP (10K) ✅ → Оптимизация (100K) ← мы здесь (Phase 1.3 ✅) → Масштабирование (1M) → Платформа (10M)
```

| Стадия | Пользователи | Суть | Критерий перехода |
|--------|-------------|------|-------------------|
| MVP | до 10K | Работающий продукт, полный цикл обучения | ✅ Locust показал деградацию при ~55 RPS |
| **Оптимизация** | **10K → 100K** | **Индексы, кэш, connection pooling, UX** | **500 RPS, p99 < 200ms, 0 errors** |
| Масштабирование | 100K → 1M | Rust gateway, event bus, read replicas, Meilisearch | 5K RPS, горизонтальное масштабирование |
| Платформа | 1M → 10M | Sharding, multi-region, видео, live streaming | 50K+ RPS, multi-region, 99.99% uptime |

---

## Навигация по документам

| # | Документ | Описание |
|---|----------|----------|
| 01 | [Видение продукта](./01-PRODUCT-VISION.md) | Бизнес-метрики, user journeys, revenue streams |
| 02 | [Архитектура](./02-ARCHITECTURE-PRINCIPLES.md) | ADR, принципы, выбор технологий |
| 03 | [Инфраструктура](./03-INFRASTRUCTURE.md) | Масштабирование, стоимость, DevOps |
| 04 | [Домены](./04-DOMAINS.md) | Bounded contexts, event matrix |
| 05 | [Стратегия данных](./05-DATA-STRATEGY.md) | Polyglot persistence, sharding, CQRS |
| 06 | [Безопасность](./06-SECURITY.md) | Threat model, compliance |
| 07 | [Видео и медиа](./07-VIDEO-MEDIA.md) | Транскодирование, CDN, live streaming |
| 08 | [Монорепа и DX](./08-MONOREPO-DX.md) | Build tools, CI/CD, testing strategy |
| 09 | [Observability](./09-OBSERVABILITY.md) | SLO, метрики, алерты |
| 10 | [Frontend](./10-FRONTEND.md) | Next.js, UI Kit, performance budgets |
| 11 | [AI Agent Standards](./11-AI-AGENT-STANDARDS.md) | MCP, context engineering, AI safety |

Версии продукта — [`versions/`](../versions/).

---

## MVP — до 10K пользователей ✅ DONE

> **Версия:** [v0.1.0-mvp](../versions/v0.1.0-mvp.md) | **Branch:** `release/v0.1.0-mvp`

### Phase 0.5 — Скелет ✅ DONE

> **Цель:** работающий каркас с auth, browsing, enrollment, payment, notifications.

| Задача | Статус |
|--------|--------|
| uv workspace (Python) | ✅ |
| Docker Compose: dev (hot reload) + prod (monitoring) | ✅ |
| Prometheus + Grafana (RPS, latency, errors) | ✅ |
| Locust сценарии (student, search, teacher, enrollment) | ✅ |
| Seed script (50K users + 100K courses + 200K enrollments + 50K payments) | ✅ |
| Shared library: config, errors, security (JWT), database (asyncpg) | ✅ |
| Identity Service: register, login, GET /me (role + is_verified) | ✅ |
| Course Service: CRUD, ILIKE search, role-based POST | ✅ |
| Enrollment Service: POST /enrollments, GET /me, GET /count | ✅ |
| Payment Service: POST /payments (mock), GET /me, GET /:id | ✅ |
| Notification Service: POST, GET /me, PATCH /read | ✅ |
| Buyer Frontend: каталог, поиск, enrollment, notifications | ✅ |
| Unit тесты: 68 тестов по 5 сервисам (→ 113 с admin) | ✅ |

**Результат:** Полный flow — регистрация → поиск → запись → оплата → уведомление. Но курс = пустая карточка.

---

### Phase 0.6 — Real MVP ✅ DONE

> **Цель:** замкнуть цикл обучения. Студент может реально учиться, преподаватель видит результат.

| # | Задача | Статус |
|---|--------|--------|
| **Контент** | | |
| 0.6.1 | Модули и уроки внутри курса (Course Service: modules + lessons) | ✅ |
| 0.6.2 | CRUD модулей и уроков (teacher) | ✅ |
| 0.6.3 | Программа курса (GET /courses/:id/curriculum) | ✅ |
| 0.6.4 | Страница урока (GET /lessons/:id — markdown + video embed) | ✅ |
| **Прогресс** | | |
| 0.6.5 | Отметка урока как пройденного (POST /progress/lessons/:id/complete) | ✅ |
| 0.6.6 | Прогресс по курсу (GET /progress/courses/:id — % completion) | ✅ |
| 0.6.7 | Автоматический completion при 100% | ⏳ Deferred |
| **Teacher tools** | | |
| 0.6.8 | GET /courses/my — курсы teacher с enrollment count | ✅ |
| 0.6.9 | PUT /courses/:id — редактирование курса | ✅ |
| 0.6.10 | Frontend: teacher dashboard page | ✅ |
| **Reviews** | | |
| 0.6.11 | POST /reviews + GET /reviews/course/:id (рейтинг 1-5 + текст) | ✅ |
| 0.6.12 | Средний рейтинг на карточке курса | ✅ |
| **Frontend** | | |
| 0.6.13 | Страница урока с markdown-рендером и video embed | ✅ |
| 0.6.14 | Прогресс-бар на странице курса | ✅ |
| 0.6.15 | Форма отзыва + список отзывов | ✅ |
| 0.6.16 | Teacher dashboard: мои курсы, кнопка "добавить урок" | ✅ |
| **Инфра** | | |
| 0.6.17 | Seed: модули + уроки для 100K courses | ✅ |
| 0.6.18 | Seed: прогресс + reviews | ✅ |
| 0.6.19 | Обновить architecture docs | ✅ |
| **Admin & UX** | | |
| 0.6.20 | Admin role + teacher verification API (Identity Service) | ✅ |
| 0.6.21 | Admin panel frontend (/admin/teachers) | ✅ |
| 0.6.22 | Teacher UX: redirect после создания, inline-редактирование уроков, баннер верификации | ✅ |
| 0.6.23 | Student UX: фидбек после записи, мобильный sidebar, breadcrumbs, кнопка завершения | ✅ |
| 0.6.24 | Seed: admin user (admin@eduplatform.com) | ✅ |

**Результат:** 113 тестов. Полный цикл: admin верифицирует teacher → teacher создаёт курс → student записывается → проходит уроки → отзыв.

---

### Phase 0.7 — Baseline & Bottlenecks ✅ DONE

> **Цель:** снять baseline метрики на Real MVP и найти первые bottleneck-и.
> Подробный отчёт — [`phases/PHASE-0.7-BASELINE.md`](../phases/PHASE-0.7-BASELINE.md).

| # | Задача | Статус |
|---|--------|--------|
| 0.7.1 | Поднять prod stack (docker-compose.prod.yml) | ✅ |
| 0.7.2 | Засеять полные данные (50K users + 100K courses + 200K enrollments + 100K reviews) | ✅ |
| 0.7.3 | Запустить Locust: 100 users, ramp 10/s, 5 минут | ✅ |
| 0.7.4 | DB pool метрики + Grafana dashboard (6 panels) | ✅ |
| 0.7.5 | Найти bottleneck-и и приоритизировать | ✅ |

### Замеренный baseline (v0.1.0)

| Метрика | Значение | Статус |
|---------|----------|--------|
| Peak RPS | ~55 | Потолок текущей архитектуры |
| Error rate | 0.5% | 80 login failures (проблема теста) |
| Course search avg | **426ms** | P0 bottleneck |
| Course search p99 | **803ms** | P0 bottleneck |
| Course list avg | 52ms | OK |
| Curriculum avg | 57ms | OK |
| DB pool (Course) | **100% saturated** | P1 bottleneck |

### Подтверждённые bottleneck-и

| # | Bottleneck | Метрика | Приоритет |
|---|-----------|---------|-----------|
| 1 | ILIKE full table scan на 100K courses | search p99 = 803ms, avg 426ms | **P0** |
| 2 | Connection pool exhaustion (Course service 5/5) | 100% saturation | **P1** |
| 3 | Login failures в Locust (user ID mismatch) | 80 failed requests | P2 |

### Опровергнутые гипотезы

| Гипотеза | Результат |
|----------|-----------|
| Curriculum JOIN тормозит | ❌ 57ms — приемлемо |
| Single-process bottleneck | ❌ 4 workers достаточно |
| Large response sizes | ❌ 52ms — приемлемо |

---

## Оптимизация — 10K → 100K пользователей 🔵 IN PROGRESS

> **Цель:** устранить замеренные bottleneck-и, сделать продукт юзабельным. Те же сервисы, но работающие быстро и надёжно.
>
> **Baseline:** 55 RPS, search p99 = 803ms, pool saturation 100%.
> **Target:** 500 RPS, p99 < 200ms, 0 errors.

### Phase 1.0 — Critical Performance (P0/P1 bottleneck-и)

> Устранение замеренных bottleneck-ов. Каждый пункт подтверждён метриками из Phase 0.7.

| # | Задача | Обоснование (метрика) | Ожидаемый эффект | Статус |
|---|--------|----------------------|-----------------|--------|
| 1.0.1 | pg_trgm + GIN index на courses.title, courses.description | search p99 = 803ms, avg 426ms (P0) | search p99: 800ms → <50ms | ✅ |
| 1.0.2 | Connection pool 5 → 20 для всех сервисов | course pool 100% saturation (P1) | saturation: 100% → <50% | ✅ |
| 1.0.3 | Fix Locust user ID ranges + seed password hash | 80 login failures (P2) | 0 test failures | ✅ |
| 1.0.4 | Перезамерить: Locust 100 users, 5 min | Валидация оптимизаций | search p99 < 100ms, pool < 50% | ✅ |

**Критерий:** search p99 < 100ms, pool saturation < 50%, 0 test errors.

---

### Phase 1.1 — Caching & Indexes

> Снижение нагрузки на БД. FK-индексы, Redis cache-aside, cursor pagination.

| # | Задача | Обоснование | Статус |
|---|--------|-------------|--------|
| 1.1.1 | FK indexes: teacher_id, course_id, module_id, student_id, user_id (все сервисы) | PostgreSQL не создаёт индексы на FK → full table scan | ✅ |
| 1.1.2 | Redis кэширование: course by id, curriculum (cache-aside, TTL 5 min) | Снижение DB reads для горячих данных | ✅ |
| 1.1.3 | Cursor-based pagination (keyset) для courses list, search, my | Offset > 10K сканирует и отбрасывает строки | ✅ |
| 1.1.4 | Перезамерить: Locust 200 users, 5 min | Валидация | ✅ |

**Результат:** 157 RPS (200 users), p99 = 51ms, search p99 = 35ms (23x vs baseline), pool 10%. Подробности — [`phases/PHASE-1.1-RESULTS.md`](../phases/PHASE-1.1-RESULTS.md).

---

### Phase 1.2 — Reliability & Security ✅ DONE

> Продукт должен быть не только быстрым, но и надёжным для реальных пользователей.

**Результат:** 146 тестов по 5 сервисам. Health checks, graceful shutdown, CORS, rate limiting, XSS sanitization, JWT refresh token rotation.

| # | Задача | Зачем | Статус |
|---|--------|-------|--------|
| 1.2.1 | JWT refresh tokens (rotation + reuse detection) | Пользователи не должны re-login каждый час | ✅ |
| 1.2.2 | Rate limiting на API (per-IP sliding window, Redis) | Защита от abuse | ✅ |
| 1.2.3 | CORS настройка (env-based origins) | Безопасность | ✅ |
| 1.2.4 | Input sanitization (XSS в course/lesson content, bleach) | UGC безопасность | ✅ |
| 1.2.5 | Graceful shutdown (SIGTERM, timeout-graceful-shutdown) | Zero-downtime deploys | ✅ |
| 1.2.6 | Health check endpoints (/health/live + /health/ready) | Container orchestration | ✅ |

---

### Phase 1.3 — UX & Product Quality ✅ DONE

> От «работает» к «приятно пользоваться».

**Результат:** 157 тестов по 5 сервисам (identity 48, course 59, enrollment 25, payment 13, notification 12). Категории + фильтрация, email verification, forgot password, auto-completion, TanStack Query, error boundaries.

| # | Задача | Зачем | Статус |
|---|--------|-------|--------|
| 1.3.1 | Error boundaries + loading states (frontend) | UX при ошибках и загрузке | ✅ |
| 1.3.2 | Email-верификация при регистрации | Качество user base | ✅ |
| 1.3.3 | Сброс пароля (forgot password flow) | Базовая функциональность | ✅ |
| 1.3.4 | Категории курсов + фильтрация + сортировка | Навигация по каталогу | ✅ |
| 1.3.5 | Автоматический completion курса при 100% уроков | Deferred из Phase 0.6 | ✅ |
| 1.3.6 | Frontend: TanStack Query + оптимистичные обновления | Отзывчивый UI | ✅ |

---

### Phase 1.4 — Финальный замер

| # | Задача | Статус |
|---|--------|--------|
| 1.4.1 | Locust: 500 users, ramp 50/s, 10 min | 🔴 |
| 1.4.2 | Зафиксировать метрики, сравнить с baseline v0.1.0 | 🔴 |
| 1.4.3 | Определить следующие bottleneck-и для Phase 2 | 🔴 |

**Критерий перехода:** стабильно 500 RPS, p99 < 200ms, 0 ошибок при 10-минутном load test.

---

## Масштабирование — 100K → 1M пользователей

> **Цель:** выход за пределы одного Python процесса.

| Задача | Статус | Зачем |
|--------|--------|-------|
| API Gateway (Rust/Axum) | 🔴 | Auth middleware, rate limiting, routing |
| Search Service (Rust) + Meilisearch | 🔴 | ILIKE/pg_trgm не масштабируется за 100K |
| NATS JetStream: event bus | 🔴 | Асинхронная связь между сервисами |
| PostgreSQL read replicas | 🔴 | Разделение read/write нагрузки |
| Video platform: upload → transcode → stream | 🔴 | Замена YouTube/Vimeo ссылок |
| Teacher Dashboard (Next.js — seller app) | 🔴 | Полноценное управление курсами |
| Protobuf контракты | 🔴 | Source of truth для межсервисного API |
| CI/CD: GitHub Actions | 🔴 | Lint → test → build → deploy |
| Kubernetes manifests | 🔴 | Auto-scaling, rolling deploys |

**Критерий перехода:** 5K RPS, горизонтальное масштабирование, event-driven.

---

## Платформа — 1M → 10M пользователей

> **Цель:** платформа enterprise-уровня. Multi-region, видео, real-time, ML.

| Задача | Статус | Зачем |
|--------|--------|-------|
| PostgreSQL → Citus (sharding) | 🔴 | Одна БД не вытянет 10M users |
| Multi-region active-active | 🔴 | Latency для юзеров в разных регионах |
| Live streaming lessons | 🔴 | Real-time обучение |
| Рекомендации (ML) | 🔴 | Персонализация каталога |
| ClickHouse для аналитики | 🔴 | Real-time dashboards для преподавателей |
| Teacher API + webhooks | 🔴 | Платформенная экосистема |
| Mobile PWA / native apps | 🔴 | 80% трафика — мобильный |
| CDN: multi-CDN strategy | 🔴 | Видео и статика по всему миру |
| Chaos engineering | 🔴 | Graceful degradation |

**Критерий завершения:** 50K+ RPS, multi-region, 99.99% uptime.

---

## Принцип принятия решений

```
Не оптимизировать ДО того, как увидел проблему в метриках.
Не масштабировать ДО того, как текущая архитектура упёрлась в потолок.
Не переписывать на Rust ДО того, как Python стал bottleneck-ом.
Каждое решение — ответ на конкретную проблему, видимую в Grafana.
```
