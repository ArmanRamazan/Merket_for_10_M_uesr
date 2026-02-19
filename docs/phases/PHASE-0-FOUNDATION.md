# Phase 0 — Foundation (Месяц 1-2)

> **Цель:** Заложить фундамент, без которого невозможен рост. Нет пользователей — только архитектура и инфраструктура.

---

## Milestone 0.1 — Скелет монорепы (Неделя 1)

| # | Задача | Ответственный | Статус |
|---|--------|--------------|--------|
| 0.1.1 | Инициализировать монорепу: Cargo workspace + Python workspace (uv) | Principal | 🔴 |
| 0.1.2 | Настроить justfile с командами: dev, build, test, lint, format | Principal | 🔴 |
| 0.1.3 | Docker Compose для инфраструктуры (PostgreSQL, Redis, NATS, Meilisearch) | Principal | 🔴 |
| 0.1.4 | CI pipeline (GitHub Actions): lint → test → build → docker push | Principal | 🔴 |
| 0.1.5 | Shared libraries: Python common (config, logging, errors), Rust common | Principal | 🔴 |
| 0.1.6 | Protobuf setup: определить первые 3 контракта, codegen pipeline | Architect | 🔴 |

---

## Milestone 0.2 — Core сервисы (Неделя 2-3)

| # | Задача | Ответственный | Статус |
|---|--------|--------------|--------|
| 0.2.1 | **Identity Service** (Python/FastAPI): регистрация, логин, JWT, refresh tokens | Principal | 🔴 |
| 0.2.2 | **API Gateway** (Rust/Axum): routing, auth middleware, rate limiting | Principal | 🔴 |
| 0.2.3 | **Catalog Service** (Python/FastAPI): CRUD товаров, категории, изображения | Principal | 🔴 |
| 0.2.4 | **Search Service** (Rust): proxy к Meilisearch, индексация, фильтры | Principal | 🔴 |
| 0.2.5 | Database schema v1: users, products, categories, images | Architect | 🔴 |
| 0.2.6 | Event bus setup: NATS JetStream, первые events (user.created, product.created) | Architect | 🔴 |

---

## Milestone 0.3 — Order и Payment flow (Неделя 4-5)

| # | Задача | Ответственный | Статус |
|---|--------|--------------|--------|
| 0.3.1 | **Orders Service** (Python): создание заказа, state machine, saga | Principal | 🔴 |
| 0.3.2 | **Payment Engine** (Rust): Stripe integration, escrow model | Principal | 🔴 |
| 0.3.3 | Cart logic: добавление, обновление, multi-seller split | Principal | 🔴 |
| 0.3.4 | Checkout flow: cart → order → payment → confirmation | Architect | 🔴 |
| 0.3.5 | Notifications Service (Python): email (welcome, order confirmation) | Principal | 🔴 |

---

## Milestone 0.4 — Video MVP (Неделя 6-7)

| # | Задача | Ответственный | Статус |
|---|--------|--------------|--------|
| 0.4.1 | Video upload flow: presigned URL → S3 → webhook | Principal | 🔴 |
| 0.4.2 | Интеграция с Cloudflare Stream (или Mux) для транскодирования | Principal | 🔴 |
| 0.4.3 | Video player component: HLS, adaptive bitrate, poster | Principal | 🔴 |
| 0.4.4 | Seller landing page: шаблон v1 (hero video + товары + CTA) | Principal | 🔴 |
| 0.4.5 | Product video: прикрепление видео к карточке товара | Principal | 🔴 |

---

## Milestone 0.5 — DevOps и Observability (Неделя 8)

| # | Задача | Ответственный | Статус |
|---|--------|--------------|--------|
| 0.5.1 | Kubernetes manifests для всех сервисов | Principal | 🔴 |
| 0.5.2 | Staging environment: auto-deploy из main branch | Principal | 🔴 |
| 0.5.3 | Monitoring: Prometheus + Grafana, базовые dashboards | Principal | 🔴 |
| 0.5.4 | Centralized logging: Loki, structured JSON logs | Principal | 🔴 |
| 0.5.5 | Health checks и readiness probes для всех сервисов | Principal | 🔴 |
| 0.5.6 | Load test: Locust сценарий, baseline performance numbers | Architect | 🔴 |

---

## Критерии завершения Phase 0

- [ ] Buyer может: зарегистрироваться → найти товар → посмотреть видео → купить → получить email
- [ ] Seller может: зарегистрироваться → добавить товары → загрузить видео → получить оплату
- [ ] Все сервисы деплоятся в K8s через CI
- [ ] Мониторинг работает, базовые алерты настроены
- [ ] Load test показывает > 1000 RPS без деградации
- [ ] Документация: ADR написаны, C4 диаграммы актуальны
