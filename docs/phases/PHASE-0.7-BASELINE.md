# Phase 0.7 — Baseline & Bottleneck Analysis

> Последнее обновление: 2026-02-21
> Статус: в процессе

---

## Цель

Снять baseline метрики на Real MVP (Phase 0.6) и найти первые bottleneck-и для приоритизации оптимизаций в Phase 1.

---

## Как запустить load test

### 1. Поднять prod stack

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Дождаться пока все healthcheck-и пройдут:
```bash
docker compose -f docker-compose.prod.yml ps
```

### 2. Засеять данные

```bash
docker compose -f docker-compose.prod.yml --profile seed up seed
```

Проверить данные:
- 1 admin + 50K users (80% students, 20% teachers)
- 100K courses (first 10K with modules + lessons)
- 200K enrollments + 50K payments
- ~100K reviews

### 3. Запустить Locust

```bash
docker compose -f docker-compose.prod.yml --profile loadtest up locust
```

Открыть http://localhost:8089

**Параметры load test:**
- Users: 100
- Ramp up: 10 users/sec
- Duration: 5 минут
- Host: оставить пустым (каждый user class задаёт свой host)

### 4. Наблюдать в Grafana

Открыть http://localhost:3000 → Dashboard → EduPlatform Services

**Что смотреть:**
- Summary row: Total RPS, Avg Latency p95, Error Rate, Active DB Connections
- Traffic: какой сервис получает больше всего нагрузки
- Latency: какие endpoints самые медленные
- DB Pool: есть ли saturation (>80% = bottleneck)

---

## Baseline Metrics

> Заполнить после первого load test

### Условия теста

| Параметр | Значение |
|----------|---------|
| Дата | |
| Users | 100 |
| Ramp up | 10/s |
| Duration | 5 min |
| Data volume | 50K users, 100K courses, 200K enrollments |
| Workers per service | 4 (uvicorn) |
| DB pool size | 5 (min=max) |
| Caching | None |
| Indexes | Only PK + UNIQUE |

### Общие показатели

| Метрика | Значение |
|---------|---------|
| Peak RPS (total) | |
| Avg RPS (steady state) | |
| Total requests | |
| Failed requests | |
| Error rate % | |

### Latency по сервисам

| Service | p50 | p95 | p99 | Max |
|---------|-----|-----|-----|-----|
| identity | | | | |
| course | | | | |
| enrollment | | | | |
| payment | | | | |
| notification | | | | |

### Latency по endpoints (top 10 slowest)

| Endpoint | p50 | p95 | p99 | RPS |
|----------|-----|-----|-----|-----|
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

### DB Pool Saturation

| Service | Pool size | Max used | Saturation % | Exhaustion events |
|---------|-----------|----------|-------------|-------------------|
| identity | 5 | | | |
| course | 5 | | | |
| enrollment | 5 | | | |
| payment | 5 | | | |
| notification | 5 | | | |

---

## Bottleneck Analysis

> Заполнить после анализа метрик

### Bottleneck #1

| Аспект | Значение |
|--------|---------|
| **Что:** | |
| **Симптом:** | |
| **Метрика:** | |
| **Причина:** | |
| **Решение:** | |
| **Приоритет:** | |

### Bottleneck #2

| Аспект | Значение |
|--------|---------|
| **Что:** | |
| **Симптом:** | |
| **Метрика:** | |
| **Причина:** | |
| **Решение:** | |
| **Приоритет:** | |

### Bottleneck #3

| Аспект | Значение |
|--------|---------|
| **Что:** | |
| **Симптом:** | |
| **Метрика:** | |
| **Причина:** | |
| **Решение:** | |
| **Приоритет:** | |

---

## Ожидаемые bottleneck-и (гипотезы)

| # | Гипотеза | Метрика для проверки | Подтвердилось? |
|---|----------|---------------------|----------------|
| 1 | ILIKE search — full table scan на 100K courses | course p99 на `/courses?q=` > 500ms | |
| 2 | Curriculum JOIN — modules + lessons per course | course p99 на `/courses/:id/curriculum` > 300ms | |
| 3 | Connection pool exhaustion (pool=5) | db_pool_saturation > 90%, 503 errors | |
| 4 | Single-process bottleneck | HTTP in-progress > 50, CPU 100% | |
| 5 | Large response sizes on course list | response_size > 50KB, high serialization time | |

---

## Решения (приоритизировать после baseline)

| Bottleneck | Решение | Ожидаемый эффект | Фаза |
|-----------|---------|-----------------|------|
| ILIKE full scan | pg_trgm + GIN index | Search p99 < 50ms | 1.0 |
| Pool exhaustion | Pool 5 → 20, PgBouncer | No 503 errors | 1.0 |
| No caching | Redis cache hot paths | -70% DB load on reads | 1.0 |
| Single worker | Already 4 workers in prod | N/A if prod config correct | — |
| Curriculum JOIN | Denormalize or cache | Curriculum p99 < 100ms | 1.0 |

---

## Grafana Dashboard Panels

Dashboard доступен по адресу http://localhost:3000 после `docker compose -f docker-compose.prod.yml up -d`

### Summary Row (stat panels)
- **Total RPS** — суммарные запросы в секунду (green < 50, yellow < 200, red > 200)
- **Avg Latency p95** — 95й перцентиль latency (green < 200ms, yellow < 500ms, red > 500ms)
- **Error Rate %** — процент 5xx ошибок (green < 1%, yellow < 5%, red > 5%)
- **Active DB Connections** — суммарные активные соединения (green < 20, red > 24)
- **Requests In Flight** — текущие обрабатываемые запросы
- **5xx Errors Total** — абсолютное число 5xx за 5 минут

### Traffic Row
- **Request Rate by Service** — RPS per service (line chart)
- **Error Rate by Service** — 5xx per service (line chart)
- **RPS by Endpoint (Top 10)** — stacked bar chart

### Latency Row
- **Latency p50/p95/p99 by Service** — три отдельных графика
- **Slowest Endpoints p99 (Top 10)** — какие endpoints самые медленные

### Database Pool Row
- **DB Pool Used vs Free** — визуализация pool utilization per service
- **DB Pool Saturation %** — used/total с цветовой шкалой (>70% yellow, >90% red)

### Resources Row
- **Requests In Progress** — concurrent requests per service
- **Avg Response Size** — размер ответов per service
