# 01 — Обзор системы

> Последнее обновление: 2026-02-21 (Phase 0.6 + Admin)
> Стадия: MVP (Phase 0) — до 10K пользователей

---

## Что есть сейчас

EduPlatform MVP — учебная платформа с полным циклом обучения. Пять бэкенд-сервисов, фронтенд и инфраструктура мониторинга/нагрузочного тестирования. Три роли: Student, Teacher, Admin. Студент может найти курс, записаться, пройти уроки, отслеживать прогресс, оставить отзыв. Преподаватель может создать курс с модулями и уроками. Администратор верифицирует преподавателей.

```
┌─────────────────────────────────────────────────────────────────┐
│                    КЛИЕНТЫ                                       │
│                                                                 │
│     Browser (http://localhost:3001)                              │
│         │                                                       │
│         ▼                                                       │
│   ┌───────────┐                                                 │
│   │  Buyer    │  Next.js 15 / Tailwind CSS 4                    │
│   │  App      │  TypeScript strict                              │
│   │  :3001    │                                                 │
│   └─────┬─────┘                                                 │
│         │  /api proxy (next.config.ts rewrites)                 │
│         │                                                       │
├─────────┼───────────────────────────────────────────────────────┤
│         │          BACKEND SERVICES                              │
│         │                                                       │
│   ┌─────┴──────────────────────────────────────────┐            │
│   │              │           │          │          │            │
│   ▼              ▼           ▼          ▼          ▼            │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐│
│ │ Identity │ │  Course  │ │Enrollment│ │Payment │ │Notificat.││
│ │  :8001   │ │  :8002   │ │  :8003   │ │ :8004  │ │  :8005   ││
│ │ Python   │ │ Python   │ │ Python   │ │Python  │ │ Python   ││
│ │ FastAPI  │ │ FastAPI  │ │ FastAPI  │ │FastAPI │ │ FastAPI  ││
│ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ └────┬─────┘│
│      │            │            │           │           │       │
├──────┼────────────┼────────────┼───────────┼───────────┼───────┤
│      │          DATA LAYER     │           │           │       │
│      │            │            │           │           │       │
│ ┌────▼───┐  ┌────▼───┐  ┌────▼───┐ ┌────▼───┐ ┌────▼───┐   │
│ │identity│  │ course │  │enroll- │ │payment │ │notifi- │   │
│ │  db    │  │   db   │  │ment db │ │  db    │ │cat. db │   │
│ │ :5433  │  │ :5434  │  │ :5435  │ │ :5436  │ │ :5437  │   │
│ └────────┘  └────────┘  └────────┘ └────────┘ └────────┘   │
│                                                              │
│              ┌──────────┐                                    │
│              │  Redis   │  :6379 (unused)                    │
│              └──────────┘                                    │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                   OBSERVABILITY                               │
│                                                              │
│   ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│   │ Prometheus │───▶│  Grafana   │    │   Locust   │        │
│   │   :9090    │    │   :3000    │    │   :8089    │        │
│   └────────────┘    └────────────┘    └────────────┘        │
└──────────────────────────────────────────────────────────────┘
```

---

## Порты

| Сервис | Порт | Протокол |
|--------|------|----------|
| Identity API | 8001 | HTTP/REST |
| Course API | 8002 | HTTP/REST |
| Enrollment API | 8003 | HTTP/REST |
| Payment API | 8004 | HTTP/REST |
| Notification API | 8005 | HTTP/REST |
| Buyer Frontend | 3001 | HTTP |
| Identity DB (PostgreSQL) | 5433 | TCP |
| Course DB (PostgreSQL) | 5434 | TCP |
| Enrollment DB (PostgreSQL) | 5435 | TCP |
| Payment DB (PostgreSQL) | 5436 | TCP |
| Notification DB (PostgreSQL) | 5437 | TCP |
| Redis | 6379 | TCP |
| Prometheus | 9090 | HTTP |
| Grafana | 3000 | HTTP |
| Locust | 8089 | HTTP |

---

## Стек технологий

| Слой | Технология | Версия | Зачем |
|------|-----------|--------|-------|
| Backend | Python / FastAPI | 3.12 / 0.115+ | Бизнес-логика, Clean Architecture |
| Frontend | Next.js / React | 15.3 / 19.1 | SSR/SSG, App Router |
| Стили | Tailwind CSS | 4.1 | Утилитарные стили |
| БД | PostgreSQL | 16 (Alpine) | Database-per-service |
| Кэш | Redis | 7 (Alpine) | Подключен, не используется (Phase 1) |
| ORM | asyncpg | 0.30+ | Raw SQL, parameterized queries |
| Auth | PyJWT + bcrypt | 2.10+ / 4.0+ | JWT HS256, bcrypt хэширование |
| Config | pydantic-settings | 2.7+ | Env vars → typed settings |
| Метрики | prometheus-fastapi-instrumentator | 7.0+ | Автоматические HTTP метрики |
| Monitoring | Prometheus + Grafana | — | Scrape 5s, dashboards |
| Load testing | Locust | — | 3 user types: StudentUser (browse, enroll, curriculum, lessons, progress), SearchUser, TeacherUser |
| Seed | asyncpg + Faker | — | 1 admin + 50K users, 100K courses, ~35K modules, ~210K lessons, 100K reviews, 50K payments, 200K enrollments |
| Packages | uv workspace | — | Python монорепа |
| Docker | Docker Compose | — | Dev (hot reload) + Prod (monitoring) |

---

## Принципы архитектуры (реализованные)

1. **Database-per-service** — у каждого сервиса своя PostgreSQL (5 БД)
2. **Clean Architecture** — routes → services → domain ← repositories
3. **JWT shared secret** — все 5 сервисов валидируют JWT самостоятельно, без обращения к Identity
4. **Клиент-оркестратор** — Frontend оркестрирует вызовы между сервисами (Payment → Enrollment → Notification)
5. **Намеренные bottleneck-и** — ILIKE без индекса, pool = 5 connections, нет кэша
6. **Роли в JWT claims** — `role` (student/teacher/admin) и `is_verified` передаются в extra_claims токена
7. **Forward-only миграции** — SQL файлы, выполняются при старте сервиса
8. **Owner check** — teacher может управлять только своими курсами/модулями/уроками (проверка teacher_id)

---

## Чего нет (намеренно, YAGNI)

| Чего нет | Почему | Когда появится |
|----------|--------|---------------|
| Индексы на поиск | Bottleneck для load testing | Когда search p99 > 300ms |
| Redis кэш | Bottleneck | Когда DB CPU > 70% |
| Connection pooling tuning | Bottleneck | Когда pool exhaustion в логах |
| API Gateway | Не нужен для 5 сервисов с прямым доступом | Phase 2 (Rust/Axum) |
| Event bus (NATS) | Нет межсервисных событий, клиент оркестрирует | Phase 2 |
| CI/CD | Локальная разработка | Phase 1 |
