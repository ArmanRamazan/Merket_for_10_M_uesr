# Phase 1 — Launch (Месяц 3-4)

> **Цель:** 0 → 100K MAU. Первые реальные пользователи, первые деньги, первые инсайты.

---

## Бизнес-цели Phase 1

| Метрика | Целевое значение |
|---------|-----------------|
| MAU | 100 000 |
| Активные продавцы | 1 000 |
| SKU в каталоге | 50 000 |
| GMV / месяц | $500K |
| Среднее время загрузки страницы | < 2 sec |
| Uptime | 99.9% |

---

## Milestone 1.1 — Go-to-Market Ready (Неделя 1-2)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 1.1.1 | SEO-оптимизация видео-лендингов: SSR, meta tags, structured data | Architect | 🔴 |
| 1.1.2 | Social sharing: Open Graph видео для Instagram, Facebook, Telegram | Principal | 🔴 |
| 1.1.3 | Mobile web оптимизация: PWA, responsive, touch gestures | Principal | 🔴 |
| 1.1.4 | Performance audit: Core Web Vitals зеленая зона для всех страниц | Architect | 🔴 |
| 1.1.5 | Seller onboarding flow: guided setup wizard, видео-инструкция | Principal | 🔴 |
| 1.1.6 | Bulk product import: CSV/Excel → каталог за 5 минут | Principal | 🔴 |

---

## Milestone 1.2 — Trust & Safety (Неделя 2-3)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 1.2.1 | Seller verification: документы, проверка, статус verified | Principal | 🔴 |
| 1.2.2 | Product moderation: AI-проверка изображений + ручная очередь | Architect | 🔴 |
| 1.2.3 | Reviews & ratings: покупатели оставляют отзывы с фото | Principal | 🔴 |
| 1.2.4 | Reporting: пользователи жалуются на товары/продавцов | Principal | 🔴 |
| 1.2.5 | Fraud detection v1: basic rules (velocity, amount, geo) | Architect | 🔴 |

---

## Milestone 1.3 — Engagement & Retention (Неделя 3-4)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 1.3.1 | Push notifications: order updates, price drops, back in stock | Principal | 🔴 |
| 1.3.2 | Email marketing integration: welcome series, abandoned cart | Principal | 🔴 |
| 1.3.3 | Wishlist / favorites: сохранение товаров | Principal | 🔴 |
| 1.3.4 | Order tracking: real-time статус доставки | Principal | 🔴 |
| 1.3.5 | Buyer-Seller messaging: чат по заказу/товару | Principal | 🔴 |

---

## Milestone 1.4 — Seller Growth Tools (Неделя 4-5)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 1.4.1 | Seller dashboard: продажи, просмотры, конверсии | Principal | 🔴 |
| 1.4.2 | Промо-инструменты v1: создание скидок, купонов | Principal | 🔴 |
| 1.4.3 | Payout system: автоматические выплаты продавцам | Architect | 🔴 |
| 1.4.4 | Seller analytics: какие товары смотрят, откуда трафик | Principal | 🔴 |

---

## Milestone 1.5 — Infrastructure Hardening (Неделя 5-6)

| # | Задача | Зона | Статус |
|---|--------|------|--------|
| 1.5.1 | Auto-scaling: HPA для всех stateless сервисов | Architect | 🔴 |
| 1.5.2 | Database: read replicas для heavy-read endpoints | Architect | 🔴 |
| 1.5.3 | CDN: настроить правильные cache headers, edge caching | Architect | 🔴 |
| 1.5.4 | Canary deployments: 5% → 25% → 100% с auto-rollback | Principal | 🔴 |
| 1.5.5 | Incident response: on-call setup, runbooks, post-mortem template | Architect | 🔴 |
| 1.5.6 | Load test: 10K concurrent users, identify bottlenecks | Architect | 🔴 |

---

## Критерии завершения Phase 1

- [ ] 100K зарегистрированных пользователей
- [ ] 1000+ активных продавцов с товарами
- [ ] Первые $500K GMV
- [ ] 99.9% uptime за последний месяц
- [ ] NPS > 30 (buyer), NPS > 40 (seller)
- [ ] P95 latency < 300ms для основных endpoints
- [ ] Zero critical security incidents
