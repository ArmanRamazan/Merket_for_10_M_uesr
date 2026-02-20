# 09 — Наблюдаемость и SLO

> Владелец: Architect / SRE
> Последнее обновление: 2026-02-20

---

## SLO (Service Level Objectives)

### Tier 1 — Критические (деньги и пользовательский опыт)
| Сервис | Метрика | SLO | Бюджет ошибок/мес |
|--------|---------|-----|-------------------|
| API Gateway | Availability | 99.95% | 21.6 мин downtime |
| API Gateway | Latency p99 | < 500ms | — |
| Payment Engine | Availability | 99.99% | 4.3 мин downtime |
| Payment Engine | Success rate | 99.5% | 0.5% failed transactions |
| Search | Latency p95 | < 100ms | — |
| Search | Availability | 99.9% | 43.2 мин downtime |
| Video Streaming | Start time | < 2 sec | — |
| Video Streaming | Buffer ratio | < 1% | — |

### Tier 2 — Важные (функциональность)
| Сервис | Метрика | SLO |
|--------|---------|-----|
| Course API | Latency p95 | < 200ms |
| Enrollment API | Latency p95 | < 300ms |
| Notifications | Delivery time | < 30 sec (email), < 5 sec (push) |
| Messaging | Delivery time | < 200ms |

### Tier 3 — Background (допускает деградацию)
| Сервис | Метрика | SLO |
|--------|---------|-----|
| Analytics Pipeline | Freshness | < 5 min lag |
| Video Transcoding | Completion time | < 10 min per video |
| Recommendations | Freshness | < 1 hour |

---

## TODO: Observability Stack

### Metrics
- [ ] 🔴 Определить стек: Prometheus + Grafana (self-hosted) или Datadog/Grafana Cloud
- [ ] 🔴 RED метрики для каждого сервиса (Rate, Errors, Duration)
- [ ] 🔴 USE метрики для инфраструктуры (Utilization, Saturation, Errors)
- [ ] 🔴 Business метрики в Grafana: revenue, enrollments/min, active users, completion rate
- [ ] 🔴 SLO dashboards: burn rate, error budget remaining

### Logging
- [ ] 🔴 Structured logging (JSON) — единый формат для Python и Rust
- [ ] 🔴 Log aggregation: Loki / Elasticsearch
- [ ] 🔴 Log levels стандарт: ERROR (alert), WARN (investigate), INFO (audit), DEBUG (dev only)
- [ ] 🔴 PII masking в логах: email, phone, card numbers → masked автоматически
- [ ] 🔴 Correlation ID: сквозной trace_id через все сервисы

### Tracing
- [ ] 🔴 Distributed tracing: OpenTelemetry → Jaeger/Tempo
- [ ] 🔴 Auto-instrumentation для Python (FastAPI) и Rust (tower/axum)
- [ ] 🔴 Trace sampling стратегия: 100% для errors, 10% для normal, 1% для health checks
- [ ] 🔴 Critical path tracing: визуализация полного пути запроса через все сервисы

### Alerting
- [ ] 🔴 Alert tiers:
  - **P0 (Page):** payment failures, API down, data loss — немедленный вызов
  - **P1 (Notify):** latency degradation, error rate spike — в Slack, 15 мин SLA
  - **P2 (Ticket):** non-critical failures, capacity warnings — создать тикет
- [ ] 🔴 Alert fatigue prevention: не более 5 алертов в день на дежурного
- [ ] 🔴 Runbooks: каждый P0/P1 алерт имеет привязанный runbook
- [ ] 🔴 On-call rotation и escalation policy

### Dashboards
- [ ] 🔴 **System Overview:** health всех сервисов, error rate, latency
- [ ] 🔴 **Business Dashboard:** revenue, enrollments, users online, completion funnel
- [ ] 🔴 **Per-service dashboards:** детали по каждому сервису
- [ ] 🔴 **Infrastructure:** CPU, memory, disk, network по нодам
- [ ] 🔴 **Cost Dashboard:** cloud spend by service, projections
