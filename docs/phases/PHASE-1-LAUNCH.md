# Phase 1 — Launch (Оптимизация, 10K → 100K MAU)

> **Цель:** устранить bottleneck-и MVP, подготовить продукт к первым реальным пользователям. Первые платные курсы, первые преподаватели, первый revenue.
>
> **Предусловие:** Phase 0 завершён — полный цикл обучения работает (уроки, прогресс, отзывы).

---

## Бизнес-цели Phase 1

| Метрика | Целевое значение |
|---------|-----------------|
| MAU | 100 000 |
| Активные преподаватели | 1 000 |
| Курсов на платформе | 10 000 |
| Revenue / месяц | $100K |
| Course completion rate | 20% |
| Среднее время загрузки страницы | < 2 sec |
| Uptime | 99.9% |

---

## Milestone 1.1 — Performance & Infrastructure ✅ DONE

> Устранение bottleneck-ов найденных в Phase 0.7. Подробности — [`PHASE-1.1-RESULTS.md`](PHASE-1.1-RESULTS.md).

| # | Задача | Статус |
|---|--------|--------|
| 1.1.1 | pg_trgm + GIN индекс на courses (title, description) | ✅ (Phase 1.0) |
| 1.1.2 | Redis кэширование: course by id, curriculum (cache-aside, TTL 5min) | ✅ |
| 1.1.3 | PgBouncer перед PostgreSQL (connection pooling) | ⏳ Deferred (pool 5/20 достаточно) |
| 1.1.4 | uvicorn workers: 4 per service | ✅ (уже было в prod compose) |
| 1.1.5 | Cursor-based pagination вместо offset | ✅ |
| 1.1.6 | FK indexes: teacher_id, course_id, module_id, student_id, user_id | ✅ (11 indexes) |

**Результат:** 157 RPS (200 users), p99 = 51ms, search p99 = 35ms (23x vs baseline), pool 10%.

---

## Milestone 1.2 — Reliability & Security ✅ DONE

> Production-readiness: security hardening и operational надёжность.

| # | Задача | Статус |
|---|--------|--------|
| 1.2.1 | JWT refresh tokens (rotation + family-based reuse detection) | ✅ |
| 1.2.2 | Rate limiting (per-IP Redis sliding window, 100/min global) | ✅ |
| 1.2.3 | CORS middleware (env-based origins) | ✅ |
| 1.2.4 | XSS sanitization (bleach) в Course service | ✅ |
| 1.2.5 | Graceful shutdown (timeout-graceful-shutdown + stop_grace_period) | ✅ |
| 1.2.6 | Health checks (/health/live + /health/ready) на всех 5 сервисах | ✅ |

**Результат:** 146 тестов по 5 сервисам.

---

## Milestone 1.3 — UX & Product Quality ✅ DONE

> От «работает» к «приятно пользоваться». Категории, фильтрация, email verification, forgot password, auto-completion, TanStack Query, error boundaries.

| # | Задача | Статус |
|---|--------|--------|
| 1.3.1 | Error boundaries + loading states (skeletons, retry) | ✅ |
| 1.3.2 | Email verification при регистрации (token hash, TTL 24h, stub) | ✅ |
| 1.3.3 | Forgot password flow (token hash, TTL 1h, rate limit 3/hr) | ✅ |
| 1.3.4 | Категории курсов + фильтрация (level, is_free) + сортировка (created_at, avg_rating, price) | ✅ |
| 1.3.5 | Auto-completion курса при 100% уроков (total_lessons, status transition) | ✅ |
| 1.3.6 | TanStack Query + optimistic updates (reviews, progress, notifications) | ✅ |

**Результат:** 157 тестов по 5 сервисам (identity 48, course 59, enrollment 25, payment 13, notification 12).

---

## Milestone 1.4 — Go-to-Market Ready

| # | Задача | Статус |
|---|--------|--------|
| 1.4.1 | SEO: SSR для каталога, meta tags, structured data (Course schema) | 🔴 |
| 1.4.2 | Social sharing: Open Graph для курсов | 🔴 |
| 1.4.3 | Mobile web: responsive, PWA | 🔴 |
| 1.4.4 | Core Web Vitals: зелёная зона для всех страниц | 🔴 |
| 1.4.5 | Teacher onboarding flow: guided wizard по созданию курса | 🔴 |

---

## Milestone 1.5 — Trust & Safety

| # | Задача | Статус |
|---|--------|--------|
| 1.5.1 | Teacher verification: загрузка документов, review queue | 🔴 |
| 1.5.2 | Course moderation: базовая проверка контента | 🔴 |
| 1.5.3 | Review moderation: фильтрация спама/оскорблений | 🔴 |
| 1.5.4 | Reporting: жалобы на курсы/преподавателей | 🔴 |

---

## Milestone 1.6 — Engagement & Retention

| # | Задача | Статус |
|---|--------|--------|
| 1.6.1 | Email уведомления: welcome, enrollment, lesson reminders | 🔴 |
| 1.6.2 | Wishlist / favorites | 🔴 |
| 1.6.3 | ~~Категории курсов + фильтры в каталоге~~ | ✅ (Phase 1.3) |
| 1.6.4 | Сертификат по завершении курса (PDF) | 🔴 |
| 1.6.5 | ~~Password reset flow~~ | ✅ (Phase 1.3) |

---

## Milestone 1.7 — Teacher Growth

| # | Задача | Статус |
|---|--------|--------|
| 1.7.1 | Seller App (Next.js): teacher dashboard | 🔴 |
| 1.7.2 | Аналитика курсов: студенты, completion rate, revenue | 🔴 |
| 1.7.3 | Stripe/YooKassa интеграция (реальные платежи) | 🔴 |
| 1.7.4 | Payout: вывод средств для преподавателей | 🔴 |
| 1.7.5 | Промо v1: купоны, скидки | 🔴 |

---

## Milestone 1.8 — Infrastructure Hardening

| # | Задача | Статус |
|---|--------|--------|
| 1.8.1 | CI/CD: GitHub Actions (lint → test → build → deploy) | 🔴 |
| 1.8.2 | Staging environment | 🔴 |
| 1.8.3 | Database backups + restore procedure | 🔴 |
| 1.8.4 | Structured logging (JSON) | 🔴 |
| 1.8.5 | Load test: 1K concurrent users | 🔴 |
| 1.8.6 | Incident response: on-call, runbooks | 🔴 |

---

## Критерии завершения Phase 1

- [ ] 100K зарегистрированных пользователей
- [ ] 1000+ активных преподавателей с курсами
- [ ] Реальные платежи работают (Stripe/YooKassa)
- [ ] 99.9% uptime за последний месяц
- [ ] P95 latency < 300ms для основных endpoints
- [ ] Стабильно 500 RPS при load test
- [ ] CI/CD pipeline работает
- [ ] Seller App (teacher dashboard) запущен
