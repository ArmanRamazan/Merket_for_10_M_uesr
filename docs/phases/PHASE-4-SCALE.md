# Phase 4 — Scale (1M → 10M MAU)

> **Цель:** тяжёлая инфраструктура для глобального масштаба. Только когда Growth
> упёрся в потолок производительности.
>
> **Предусловие:** Phase 3 завершена — revenue > $100K/мес, 1M MAU.

---

## Бизнес-цели Phase 4

| Метрика | Целевое значение |
|---------|-----------------|
| MAU | 10 000 000 |
| Revenue / мес | $18M |
| Latency p99 | < 200ms globally |
| Uptime | 99.99% |

---

## Milestone 4.1 — Rust Performance Layer

| # | Задача | Статус |
|---|--------|--------|
| 4.1.1 | API Gateway (Rust/Axum): auth, routing, rate limiting | 🔴 |
| 4.1.2 | Search Service (Rust) + Meilisearch | 🔴 |
| 4.1.3 | Protobuf contracts (gRPC) | 🔴 |

---

## Milestone 4.2 — Event-Driven Architecture

| # | Задача | Статус |
|---|--------|--------|
| 4.2.1 | NATS JetStream event bus | 🔴 |
| 4.2.2 | Async events between all services | 🔴 |
| 4.2.3 | Event sourcing for learning events | 🔴 |

---

## Milestone 4.3 — Video Platform

| # | Задача | Статус |
|---|--------|--------|
| 4.3.1 | Video upload + transcode pipeline (Rust) | 🔴 |
| 4.3.2 | Adaptive HLS streaming | 🔴 |
| 4.3.3 | Multi-CDN strategy | 🔴 |
| 4.3.4 | Auto-transcription + subtitles | 🔴 |

---

## Milestone 4.4 — Database Scale

| # | Задача | Статус |
|---|--------|--------|
| 4.4.1 | PostgreSQL read replicas | 🔴 |
| 4.4.2 | Citus sharding (courses, enrollments) | 🔴 |
| 4.4.3 | ClickHouse for analytics | 🔴 |

---

## Milestone 4.5 — AI Scale

| # | Задача | Статус |
|---|--------|--------|
| 4.5.1 | Self-hosted SLM (replace 80% of API calls) | 🔴 |
| 4.5.2 | Fine-tuned tutor model on our interaction data | 🔴 |
| 4.5.3 | Multi-language AI (auto-translate, localized tutor) | 🔴 |

---

## Milestone 4.6 — Global Infrastructure

| # | Задача | Статус |
|---|--------|--------|
| 4.6.1 | Kubernetes auto-scaling | 🔴 |
| 4.6.2 | Multi-region active-active | 🔴 |
| 4.6.3 | Global load balancing (GeoDNS) | 🔴 |
| 4.6.4 | Mobile app (PWA → native) | 🔴 |
