# 05 — Стратегия данных

> Владелец: Architect / Data Lead
> Последнее обновление: 2026-02-20

---

## Оценка объемов данных при 10M DAU

| Тип данных | Объем на 10M DAU | Рост/месяц | Хранилище |
|-----------|-----------------|-----------|-----------|
| Пользователи | 30M записей, ~30GB | +5% | PostgreSQL |
| Курсы (metadata) | 1M записей, ~10GB | +8% | PostgreSQL |
| Уроки и материалы | 10M записей, ~50GB | +10% | PostgreSQL + S3 |
| Видео (оригиналы) | 5M файлов, ~500TB | +20% | S3/R2 |
| Видео (транскодированные) | 25M файлов, ~1PB | +20% | CDN Edge |
| Enrollments | 200M записей, ~200GB | +12% | PostgreSQL |
| Сообщения | 1B записей, ~2TB | +15% | PostgreSQL + Archive |
| Events (analytics) | 50B событий, ~10TB | +20% | ClickHouse |
| Search index | ~10GB active | +10% | Meilisearch/ES |
| Cache (hot data) | ~50GB | stable | Redis |

---

## TODO: Data Architecture

### Стратегия хранения
- [ ] 🔴 Определить polyglot persistence map: какие данные в каком хранилище и почему
- [ ] 🔴 PostgreSQL sharding стратегия (Citus): определить shard keys для каждой таблицы
- [ ] 🔴 Стратегия архивации: неактивные enrollments старше 2 лет → cold storage, но доступны через API
- [ ] 🔴 Data partitioning: time-based partitions для events, enrollments, messages
- [ ] 🔴 Определить retention policy для каждого типа данных

### Event Streaming
- [ ] 🔴 Определить event schema registry (protobuf definitions в монорепе)
- [ ] 🔴 Event versioning стратегия: как эволюционировать events без breaking changes
- [ ] 🔴 Dead letter queue стратегия: что делать с unprocessable events
- [ ] 🔴 Event replay capability: возможность переиграть события за последние 30 дней

### CQRS где нужно
- [ ] 🔴 Каталог курсов: write model (PostgreSQL) + read model (Search Index + Redis)
- [ ] 🔴 Feed/рекомендации: pre-computed read models в Redis
- [ ] 🔴 Аналитика преподавателей: pre-aggregated materialized views в ClickHouse

### Data Pipeline
- [ ] 🔴 CDC (Change Data Capture) для синхронизации PostgreSQL → ClickHouse
- [ ] 🔴 CDC для синхронизации PostgreSQL → Search Index
- [ ] 🔴 ETL pipeline для business reports (daily/weekly)
- [ ] 🔴 Real-time event ingestion pipeline: client → API → NATS → ClickHouse

### Data Quality
- [ ] 🔴 Schema validation на уровне event bus (отвергать невалидные события)
- [ ] 🔴 Data consistency checks: scheduled jobs для выявления расхождений между сервисами
- [ ] 🔴 Monitoring: алерты на аномалии в данных (резкий рост/падение метрик)

### Compliance и Privacy
- [ ] 🔴 GDPR/PDPA стратегия: right to deletion, data export
- [ ] 🔴 PII encryption at rest
- [ ] 🔴 Data access audit logging
- [ ] 🔴 Anonymization pipeline для analytics (убирать PII из событий)
