# Phase 1 — Launch (Оптимизация, 10K → 100K MAU)

> **Цель:** устранить bottleneck-и MVP, подготовить продукт к первым реальным пользователям. Первые платные курсы, первые преподаватели, первый revenue.
>
> **Предусловие:** Phase 0 завершён — полный цикл обучения работает (уроки, прогресс, отзывы).

---

## Бизнес-цели Phase 1

| Метрика                                              | Целевое значение |
| ----------------------------------------------------------- | ------------------------------- |
| MAU                                                         | 100 000                         |
| Активные преподаватели                 | 1 000                           |
| Курсов на платформе                        | 10 000                          |
| Revenue / месяц                                        | $100K                           |
| Course completion rate                                      | 20%                             |
| Среднее время загрузки страницы | < 2 sec                         |
| Uptime                                                      | 99.9%                           |

---

## Milestone 1.1 — Performance & Infrastructure ✅ DONE

> Устранение bottleneck-ов найденных в Phase 0.7. Подробности — [`PHASE-1.1-RESULTS.md`](PHASE-1.1-RESULTS.md).

| #     | Задача                                                                   | Статус                                 |
| ----- | ------------------------------------------------------------------------------ | -------------------------------------------- |
| 1.1.1 | pg_trgm + GIN индекс на courses (title, description)                   | ✅ (Phase 1.0)                               |
| 1.1.2 | Redis кэширование: course by id, curriculum (cache-aside, TTL 5min) | ✅                                           |
| 1.1.3 | PgBouncer перед PostgreSQL (connection pooling)                           | ⏳ Deferred (pool 5/20 достаточно) |
| 1.1.4 | uvicorn workers: 4 per service                                                 | ✅ (уже было в prod compose)         |
| 1.1.5 | Cursor-based pagination вместо offset                                    | ✅                                           |
| 1.1.6 | FK indexes: teacher_id, course_id, module_id, student_id, user_id              | ✅ (11 indexes)                              |

**Результат:** 157 RPS (200 users), p99 = 51ms, search p99 = 35ms (23x vs baseline), pool 10%.

---

## Milestone 1.2 — Reliability & Security ✅ DONE

> Production-readiness: security hardening и operational надёжность.

| #     | Задача                                                                  | Статус |
| ----- | ----------------------------------------------------------------------------- | ------------ |
| 1.2.1 | JWT refresh tokens (rotation + family-based reuse detection)                  | ✅           |
| 1.2.2 | Rate limiting (per-IP Redis sliding window, 100/min global)                   | ✅           |
| 1.2.3 | CORS middleware (env-based origins)                                           | ✅           |
| 1.2.4 | XSS sanitization (bleach) в Course service                                   | ✅           |
| 1.2.5 | Graceful shutdown (timeout-graceful-shutdown + stop_grace_period)             | ✅           |
| 1.2.6 | Health checks (/health/live + /health/ready) на всех 5 сервисах | ✅           |

**Результат:** 146 тестов по 5 сервисам.

---

## Milestone 1.3 — UX & Product Quality ✅ DONE

> От «работает» к «приятно пользоваться». Категории, фильтрация, email verification, forgot password, auto-completion, TanStack Query, error boundaries.

| #     | Задача                                                                                                                   | Статус |
| ----- | ------------------------------------------------------------------------------------------------------------------------------ | ------------ |
| 1.3.1 | Error boundaries + loading states (skeletons, retry)                                                                           | ✅           |
| 1.3.2 | Email verification при регистрации (token hash, TTL 24h, stub)                                                   | ✅           |
| 1.3.3 | Forgot password flow (token hash, TTL 1h, rate limit 3/hr)                                                                     | ✅           |
| 1.3.4 | Категории курсов + фильтрация (level, is_free) + сортировка (created_at, avg_rating, price) | ✅           |
| 1.3.5 | Auto-completion курса при 100% уроков (total_lessons, status transition)                                         | ✅           |
| 1.3.6 | TanStack Query + optimistic updates (reviews, progress, notifications)                                                         | ✅           |

**Результат:** 157 тестов по 5 сервисам (identity 48, course 59, enrollment 25, payment 13, notification 12).

---

## Milestones 1.4–1.8 — Перенесены

> **Стратегический поворот (2026-02-24):** Фокус сместился с инфраструктурной оптимизации на продуктовую дифференциацию. Задачи milestones 1.4–1.8 перенесены в новые фазы:
>
> - SEO, Teacher Growth, Payments → **Phase 3 (Growth)** — `PHASE-3-GROWTH.md`
> - CI/CD, Staging, Backups → **Phase 3 (Growth)**, Milestone 3.4
> - Trust & Safety, Moderation → **Phase 3 (Growth)**, Milestone 3.5
>
> **Следующий шаг:** Phase 2 — Learning Intelligence (AI-квизы, spaced repetition, Сократический тьютор). См. `PHASE-2-LEARNING-INTELLIGENCE.md`.

---

## Критерии завершения Phase 1 (Foundation)

- [x] 5 Python сервисов работают (Identity, Course, Enrollment, Payment, Notification)
- [x] 157 unit тестов проходят
- [x] JWT auth + refresh tokens + email verification
- [x] Redis кэширование + rate limiting
- [x] Frontend (Buyer App) с TanStack Query + Error boundaries
- [x] Load test baseline: 157 RPS, p99 = 51ms
- [x] Docker Compose dev + prod конфигурации
- [x] Demo script проходит полный user journey
