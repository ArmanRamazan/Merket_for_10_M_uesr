# Phase 2 — Growth (Месяц 5-8)

> **Цель:** 100K → 1M MAU. Масштабирование, которое не ломает UX. Формирование flywheel: больше преподавателей → больше курсов → больше студентов → больше преподавателей.

---

## Бизнес-цели Phase 2

| Метрика | Целевое значение |
|---------|-----------------|
| MAU | 1 000 000 |
| Активные преподаватели | 10 000 |
| Курсов на платформе | 100 000 |
| Revenue / месяц | $5M |
| DAU/MAU stickiness | 25% |
| Course completion rate | 35% |
| Video lesson engagement | 70% avg watch time |

---

## Milestone 2.1 — Personalization Engine (Месяц 5)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.1.1 | Recommendation engine v1: "Похожие курсы" на основе collaborative filtering | Architect | 🔴 |
| 2.1.2 | Personalized feed: главная страница адаптируется под интересы и прогресс студента | Architect | 🔴 |
| 2.1.3 | Search ranking v2: персонализация результатов (enrollment history, интересы) | Principal | 🔴 |
| 2.1.4 | "Продолжить обучение" и "Студенты также изучают" виджеты | Principal | 🔴 |
| 2.1.5 | A/B testing infrastructure: feature flags + metric tracking + statistical analysis | Architect | 🔴 |

---

## Milestone 2.2 — Scale Database Layer (Месяц 5-6)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.2.1 | PostgreSQL → Citus: внедрить distributed PostgreSQL для courses и enrollments | Architect | 🔴 |
| 2.2.2 | Определить shard keys: courses по teacher_id, enrollments по student_id | Architect | 🔴 |
| 2.2.3 | Connection pooling optimization: PgBouncer tuning | Principal | 🔴 |
| 2.2.4 | Query optimization: EXPLAIN ANALYZE для всех slow queries (> 100ms) | Principal | 🔴 |
| 2.2.5 | ClickHouse для analytics: миграция аналитических запросов из PostgreSQL | Architect | 🔴 |
| 2.2.6 | Data archival: неактивные курсы и старые enrollments → партиции, cold storage | Architect | 🔴 |

---

## Milestone 2.3 — Video Platform v2 (Месяц 6-7)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.3.1 | Собственный Rust transcoding pipeline (уход от SaaS) | Architect | 🔴 |
| 2.3.2 | Video lessons: загрузка, транскодирование, adaptive streaming (HLS) | Principal | 🔴 |
| 2.3.3 | Video analytics: время просмотра, completion rate, drop-off points | Architect | 🔴 |
| 2.3.4 | AI thumbnails: автовыбор лучшего кадра для превью урока | Principal | 🔴 |
| 2.3.5 | Video SEO: sitemap для видео-уроков, schema.org Course/VideoObject | Principal | 🔴 |
| 2.3.6 | Cost optimization: smart quality selection, bandwidth prediction | Architect | 🔴 |

---

## Milestone 2.4 — Platform Economics (Месяц 7)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.4.1 | Promoted courses: преподаватели платят за продвижение в поиске (CPC модель) | Architect | 🔴 |
| 2.4.2 | Teacher subscription tiers: Free / Pro / Enterprise — разные лимиты и фичи | Architect | 🔴 |
| 2.4.3 | Dynamic pricing tools: автоматические скидки, flash sales, bundles | Principal | 🔴 |
| 2.4.4 | Teacher analytics v2: competitor benchmarking, pricing suggestions | Principal | 🔴 |
| 2.4.5 | Financial dashboard: unit economics, CAC, LTV, payback period | Architect | 🔴 |

---

## Milestone 2.5 — Platform Reliability (Месяц 8)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.5.1 | Multi-region: primary + hot standby в другом регионе | Architect | 🔴 |
| 2.5.2 | Chaos engineering: GameDay exercises, monthly failure injection | Architect | 🔴 |
| 2.5.3 | Graceful degradation: план что отключать при перегрузке (рекомендации → поиск → каталог) | Architect | 🔴 |
| 2.5.4 | Circuit breakers: между каждой парой сервисов | Principal | 🔴 |
| 2.5.5 | Rate limiting v2: per-user, per-teacher, per-endpoint, adaptive | Principal | 🔴 |
| 2.5.6 | Performance regression detection в CI: benchmark comparison per commit | Principal | 🔴 |

---

## Критерии завершения Phase 2

- [ ] 1M MAU устойчиво
- [ ] System выдерживает 50K concurrent users без деградации
- [ ] Recommendations повышают enrollment на 15%+ (A/B verified)
- [ ] Video platform на собственном стеке, cost < $5K/мес на текущих объемах
- [ ] Promoted courses приносят > 10% revenue
- [ ] 99.95% uptime
- [ ] RTO < 15 мин для любого компонента
