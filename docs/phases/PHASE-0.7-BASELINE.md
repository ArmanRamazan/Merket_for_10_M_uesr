# Phase 0.7 — Baseline & Bottleneck Analysis

> Последнее обновление: 2026-02-21
> Статус: ✅ завершён

---

## Цель

Снять baseline метрики на Real MVP (Phase 0.6) и найти первые bottleneck-и для приоритизации оптимизаций в Phase 1.

---

## Как запустить load test

### 1. Поднять prod stack

```bash
docker compose -f docker-compose.prod.yml down -v --remove-orphans
docker network prune -f
docker compose -f docker-compose.prod.yml up -d --build --remove-orphans
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
docker compose -f docker-compose.prod.yml --profile loadtest up -d locust
```

Открыть http://localhost:8089 или запустить через API:
```bash
curl -X POST http://localhost:8089/swarm \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_count=100&spawn_rate=10&run_time=5m"
```

### 4. Наблюдать в Grafana

Открыть http://localhost:3000 → Dashboard → EduPlatform Services

---

## Baseline Metrics

### Условия теста

| Параметр | Значение |
|----------|---------|
| Дата | 2026-02-21 |
| Users | 100 |
| Ramp up | 10/s |
| Duration | 5 min |
| Data volume | 50K users, 100K courses, 200K enrollments, 100K reviews |
| Workers per service | 4 (uvicorn) |
| DB pool size | 5 (min=max) |
| Caching | None |
| Indexes | Only PK + UNIQUE |

### Общие показатели

| Метрика | Значение |
|---------|---------|
| Peak RPS (total) | ~55 |
| Avg RPS (steady state) | 54.7 |
| Total requests | 16,085 |
| Failed requests | 80 (all login failures) |
| Error rate % | 0.5% |

### Latency по сервисам (Prometheus p99, 5m window)

| Service | p99 | Комментарий |
|---------|-----|-------------|
| **course** | **803ms** | **BOTTLENECK — search ILIKE** |
| identity | 99ms | Login bcrypt ~500ms, но мало запросов |
| enrollment | 99ms | Нормально |
| payment | 99ms | Нормально |
| notification | 99ms | Нет трафика в тесте |

### Latency по endpoints (Locust, top 10 slowest)

| Endpoint | Avg | Median | RPS | Fails |
|----------|-----|--------|-----|-------|
| `/login` (identity) | 591-608ms | 480-500ms | ~0 | 80 (100%) |
| **`/courses?q=:term` (search)** | **426ms** | **420ms** | **10.5** | **0** |
| `/courses` (list) | 52ms | 44ms | 11.6 | 0 |
| `/courses/:id/curriculum` | 57ms | 49ms | 6.6 | 0 |
| `/courses/:id` | 51ms | 46ms | 6.5 | 0 |
| `/lessons/:id` | — | — | — | — |

### DB Pool Saturation

| Service | Pool size | Max used | Saturation % | Комментарий |
|---------|-----------|----------|-------------|-------------|
| **course** | **5** | **5** | **100%** | **BOTTLENECK — pool exhaustion** |
| identity | 5 | 0 | 0% | Мало запросов |
| enrollment | 5 | 0 | 0% | Мало запросов |
| payment | 5 | 0 | 0% | Мало запросов |
| notification | 5 | 0 | 0% | Нет трафика |

---

## Bottleneck Analysis

### Bottleneck #1 — ILIKE Search (CRITICAL)

| Аспект | Значение |
|--------|---------|
| **Что:** | Поиск курсов `/courses?q=:term` |
| **Симптом:** | avg 426ms, median 420ms при 10 RPS |
| **Метрика:** | Course service p99 = 803ms |
| **Причина:** | `ILIKE '%query%'` выполняет full table scan на 100K rows без индекса |
| **Решение:** | pg_trgm extension + GIN index на `courses.title` и `courses.description` |
| **Приоритет:** | P0 — самый медленный endpoint, блокирует 20% трафика |

### Bottleneck #2 — Connection Pool Exhaustion (HIGH)

| Аспект | Значение |
|--------|---------|
| **Что:** | Course service DB pool = 5 connections, все заняты |
| **Симптом:** | db_pool_used_connections = 5/5 (100% saturation) |
| **Метрика:** | db_pool_saturation = 100% для course service |
| **Причина:** | Медленные ILIKE запросы держат connection дольше, pool=5 слишком мал для 4 workers |
| **Решение:** | Увеличить pool до 20, после решения Bottleneck #1 пересмотреть |
| **Приоритет:** | P1 — усугубляет Bottleneck #1, может вызвать 503 при росте нагрузки |

### Bottleneck #3 — Login Failures (MEDIUM)

| Аспект | Значение |
|--------|---------|
| **Что:** | 100% login failures в Locust |
| **Симптом:** | 80 failed requests, все на /login |
| **Метрика:** | error_rate = 0.5% overall |
| **Причина:** | Locust users используют случайные user IDs, некоторые не существуют в seed data. bcrypt = 500ms+ per attempt |
| **Решение:** | Исправить Locust user ID range; bcrypt latency — ожидаемая (security), не оптимизировать |
| **Приоритет:** | P2 — проблема в тесте, не в сервисе |

---

## Ожидаемые bottleneck-и (гипотезы)

| # | Гипотеза | Метрика для проверки | Подтвердилось? |
|---|----------|---------------------|----------------|
| 1 | ILIKE search — full table scan на 100K courses | course p99 = 803ms, search avg 426ms | ✅ **Да** — главный bottleneck |
| 2 | Curriculum JOIN — modules + lessons per course | curriculum avg = 57ms | ❌ Нет — приемлемо |
| 3 | Connection pool exhaustion (pool=5) | course pool 100% saturation | ✅ **Да** — следствие #1 |
| 4 | Single-process bottleneck | Нет данных CPU, но in-progress нормальный | ❌ Нет — 4 workers достаточно |
| 5 | Large response sizes on course list | list avg 52ms | ❌ Нет — приемлемо |

---

## Решения (приоритизированные по результатам)

| # | Bottleneck | Решение | Ожидаемый эффект | Приоритет |
|---|-----------|---------|-----------------|-----------|
| 1 | ILIKE full scan | pg_trgm + GIN index на title, description | Search p99: 800ms → <50ms | P0 |
| 2 | Pool exhaustion | Pool 5 → 20 для всех сервисов | Saturation 100% → <50% | P1 |
| 3 | No caching on course list | Redis cache для `/courses` и `/courses/:id` | DB reads -50-70% | P2 |
| 4 | Login test failures | Fix Locust user ID ranges | 0 test failures | P2 |

---

## Grafana Dashboard Panels

Dashboard: http://localhost:3000 → EduPlatform Services

### Summary Row (stat panels)
- **Total RPS** — суммарные запросы (green < 50, yellow < 200, red > 200)
- **Avg Latency p95** — 95й перцентиль (green < 200ms, yellow < 500ms, red > 500ms)
- **Error Rate %** — процент 5xx (green < 1%, yellow < 5%, red > 5%)
- **Active DB Connections** — активные соединения (green < 20, red > 24)
- **Requests In Flight** — текущие запросы
- **5xx Errors Total** — абсолютное число 5xx за 5 минут

### Traffic Row
- **Request Rate by Service** — RPS per service
- **Error Rate by Service** — 5xx per service
- **RPS by Endpoint (Top 10)** — stacked bar chart

### Latency Row
- **Latency p50/p95/p99 by Service** — три графика
- **Slowest Endpoints p99 (Top 10)** — самые медленные endpoints

### Database Pool Row
- **DB Pool Used vs Free** — pool utilization per service
- **DB Pool Saturation %** — used/total с цветовой шкалой (>70% yellow, >90% red)

### Resources Row
- **Requests In Progress** — concurrent requests per service
- **Avg Response Size** — размер ответов per service
