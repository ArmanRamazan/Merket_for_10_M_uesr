# Phase 2 — Growth (Месяц 5-8)

> **Цель:** 100K → 1M MAU. Масштабирование, которое не ломает UX. Формирование flywheel: больше продавцов → больше товаров → больше покупателей → больше продавцов.

---

## Бизнес-цели Phase 2

| Метрика | Целевое значение |
|---------|-----------------|
| MAU | 1 000 000 |
| Активные продавцы | 10 000 |
| SKU в каталоге | 2 000 000 |
| GMV / месяц | $15M |
| DAU/MAU stickiness | 25% |
| Repeat purchase rate (30d) | 35% |
| Video landing conversion | 5% |

---

## Milestone 2.1 — Personalization Engine (Месяц 5)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.1.1 | Recommendation engine v1: "Похожие товары" на основе collaborative filtering | Architect | 🔴 |
| 2.1.2 | Personalized feed: главная страница адаптируется под поведение пользователя | Architect | 🔴 |
| 2.1.3 | Search ranking v2: персонализация результатов (purchase history, browse history) | Principal | 🔴 |
| 2.1.4 | "Recently viewed" и "Customers also bought" виджеты | Principal | 🔴 |
| 2.1.5 | A/B testing infrastructure: feature flags + metric tracking + statistical analysis | Architect | 🔴 |

---

## Milestone 2.2 — Scale Database Layer (Месяц 5-6)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.2.1 | PostgreSQL → Citus: внедрить distributed PostgreSQL для products и orders | Architect | 🔴 |
| 2.2.2 | Определить shard keys: products по seller_id, orders по buyer_id | Architect | 🔴 |
| 2.2.3 | Connection pooling optimization: PgBouncer tuning | Principal | 🔴 |
| 2.2.4 | Query optimization: EXPLAIN ANALYZE для всех slow queries (> 100ms) | Principal | 🔴 |
| 2.2.5 | ClickHouse для analytics: миграция аналитических запросов из PostgreSQL | Architect | 🔴 |
| 2.2.6 | Data archival: заказы старше 1 года → партиции, cold storage | Architect | 🔴 |

---

## Milestone 2.3 — Video Platform v2 (Месяц 6-7)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.3.1 | Собственный Rust transcoding pipeline (уход от SaaS) | Architect | 🔴 |
| 2.3.2 | Short-form video: 15-30 сек вертикальные видео товаров (Reels-формат) | Principal | 🔴 |
| 2.3.3 | Video analytics: время просмотра, completion rate, click-through → purchase | Architect | 🔴 |
| 2.3.4 | AI thumbnails: автовыбор лучшего кадра для превью | Principal | 🔴 |
| 2.3.5 | Video SEO: sitemap для видео, schema.org VideoObject | Principal | 🔴 |
| 2.3.6 | Cost optimization: smart quality selection, bandwidth prediction | Architect | 🔴 |

---

## Milestone 2.4 — Marketplace Economics (Месяц 7)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.4.1 | Promoted listings: продавцы платят за продвижение в поиске (CPC модель) | Architect | 🔴 |
| 2.4.2 | Seller subscription tiers: Free / Pro / Enterprise — разные лимиты и фичи | Architect | 🔴 |
| 2.4.3 | Dynamic pricing tools: автоматические скидки, flash sales | Principal | 🔴 |
| 2.4.4 | Seller analytics v2: competitor benchmarking, pricing suggestions | Principal | 🔴 |
| 2.4.5 | Financial dashboard: unit economics, CAC, LTV, payback period | Architect | 🔴 |

---

## Milestone 2.5 — Platform Reliability (Месяц 8)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 2.5.1 | Multi-region: primary + hot standby в другом регионе | Architect | 🔴 |
| 2.5.2 | Chaos engineering: GameDay exercises, monthly failure injection | Architect | 🔴 |
| 2.5.3 | Graceful degradation: план что отключать при перегрузке (рекомендации → поиск → каталог) | Architect | 🔴 |
| 2.5.4 | Circuit breakers: между каждой парой сервисов | Principal | 🔴 |
| 2.5.5 | Rate limiting v2: per-user, per-seller, per-endpoint, adaptive | Principal | 🔴 |
| 2.5.6 | Performance regression detection в CI: benchmark comparison per commit | Principal | 🔴 |

---

## Критерии завершения Phase 2

- [ ] 1M MAU устойчиво
- [ ] System выдерживает 50K concurrent users без деградации
- [ ] Recommendations повышают конверсию на 15%+ (A/B verified)
- [ ] Video platform на собственном стеке, cost < $5K/мес на текущих объемах
- [ ] Promoted listings приносят > 10% revenue
- [ ] 99.95% uptime
- [ ] RTO < 15 мин для любого компонента
