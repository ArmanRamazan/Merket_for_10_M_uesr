# Monorepo Structure

> Принципы: **YAGNI** — только то, что нужно сейчас. **SRP** — один сервис = один домен. **DIP** — сервисы зависят от контрактов (proto), не друг от друга.

---

## Дерево

```
marketplace/
│
├── proto/                         # Контракты между сервисами (source of truth)
│   ├── identity/v1/               #   Auth, users
│   ├── catalog/v1/                #   Products, categories, inventory
│   ├── orders/v1/                 #   Orders, cart
│   └── events/v1/                 #   Domain events (async)
│
├── libs/                          # Shared код (минимум, только DRY)
│   ├── py/
│   │   ├── common/                #   Config, logging, errors, middleware
│   │   └── db/                    #   DB connection, migration helpers
│   └── rs/
│       ├── common/src/            #   Error types, config, tracing setup
│       └── proto-gen/src/         #   Сгенерированный код из proto/
│
├── services/                      # Deployable сервисы
│   ├── py/                        # Python сервисы (бизнес-логика)
│   │   ├── identity/              #   Регистрация, auth, JWT, roles
│   │   ├── catalog/               #   CRUD товаров, категории, inventory
│   │   ├── orders/                #   Заказы, корзина, state machine
│   │   └── notifications/         #   Email, push (event consumer)
│   └── rs/                        # Rust сервисы (performance-critical)
│       ├── api-gateway/           #   Routing, auth check, rate limiting
│       ├── search/                #   Поисковый proxy + ranking
│       ├── video-processor/       #   Upload, transcode, stream
│       └── payment-engine/        #   Транзакции, escrow, payouts
│
├── apps/                          # Frontend приложения (Next.js)
│   ├── buyer/                     #   Покупательский сайт (SSR/SSG/Client)
│   └── seller/                    #   Дашборд продавца (Client-side)
│
├── packages/                      # Shared frontend пакеты
│   ├── ui/                        #   UI Kit: Radix + Tailwind компоненты
│   ├── api-client/                #   Typed API client (codegen из OpenAPI)
│   └── shared/                    #   Validators, formatters, constants
│
├── deploy/                        # Infrastructure
│   ├── docker/                    #   Dockerfiles per service
│   └── k8s/base/                  #   K8s manifests
│
├── tools/                         # Dev utilities
│   └── seed/                      #   Database seeding scripts
│
└── docs/                          # Документация (goals, phases, ADR)
```

---

## Почему именно так

### Что есть и почему

| Решение | Принцип | Обоснование |
|---------|---------|-------------|
| `proto/` на верхнем уровне | **DIP** | Контракты — это абстракции. Сервисы зависят от них, не друг от друга |
| `services/py/` и `services/rs/` | **SRP** | Четкое разделение по языку и runtime. Разные build pipelines |
| `libs/` минимальный | **YAGNI** | Только config, logging, db utils. Абстракции появятся когда будет 2+ потребителя |
| Каждый Python сервис: `routes → services → domain → repositories` | **SRP + DIP** | Clean Architecture слои. Domain не знает про HTTP и БД |
| `events/v1/` в proto | **OCP** | Новые события добавляются без изменения существующих сервисов |
| `deploy/` отдельно от сервисов | **SRP** | Инфраструктура не смешивается с бизнес-логикой |
| `apps/` для фронтенда, `packages/` для shared | **SRP** | Buyer и Seller — разные приложения с разными требованиями к рендерингу и аудиториями |
| `packages/ui/` отдельно | **DRY + OCP** | Единый UI Kit для всех приложений. Новый app использует готовые компоненты |
| `packages/api-client/` с codegen | **DIP** | Фронтенд зависит от сгенерированного контракта, не от деталей реализации API |

### Чего НЕТ и почему (YAGNI)

| Чего нет | Когда появится | Триггер для создания |
|----------|---------------|---------------------|
| `services/py/messaging/` | Phase 1 | Когда buyer-seller chat станет приоритетом |
| `services/py/moderation/` | Phase 1 | Когда будет > 1000 товаров и нужна модерация |
| `services/py/analytics-api/` | Phase 2 | Когда seller dashboard потребует аналитику |
| `services/py/seller-tools/` | Phase 1 | Когда seller dashboard станет отдельным сервисом (пока внутри catalog) |
| `services/rs/feed-builder/` | Phase 2 | Когда рекомендации станут приоритетом |
| `workers/` директория | Когда вырастет | Пока background jobs живут внутри сервисов. Выделим когда нужна независимая масштабируемость |
| `libs/py/testing/` | Когда будет boilerplate | Пока fixtures живут в `tests/` каждого сервиса. Выделим когда увидим дублирование |
| `terraform/` | Phase 1 | Пока K8s manifests хватает. IaC когда будет multi-env |
| `apps/admin/` | Phase 1 | Admin panel когда появится модерация и финансовый контроль |

---

## Внутренняя структура Python сервиса

```
services/py/{service}/
├── app/
│   ├── routes/          # HTTP handlers (presentation layer)
│   │   └──              #   Принимает request → вызывает service → возвращает response
│   │                    #   Здесь: валидация input, HTTP коды, сериализация
│   │
│   ├── services/        # Use cases (application layer)
│   │   └──              #   Оркестрация бизнес-логики
│   │                    #   Вызывает domain + repositories + external services
│   │                    #   Транзакции и координация
│   │
│   ├── domain/          # Бизнес-правила (domain layer)
│   │   └──              #   Entities, Value Objects, Domain Events
│   │                    #   НЕ зависит от фреймворков, БД, HTTP
│   │                    #   Чистый Python, максимум dataclasses
│   │
│   └── repositories/    # Доступ к данным (infrastructure layer)
│       └──              #   Абстрактный интерфейс + SQL реализация
│                        #   Маппинг domain entities ↔ DB rows
│
├── tests/               # Тесты рядом с кодом
│   └──                  #   Unit: мокают repositories
│                        #   Integration: реальная БД (testcontainers)
│
└── migrations/          # SQL миграции (alembic или raw SQL)
```

**Правило зависимостей** (Dependency Rule):
```
routes → services → domain ← repositories
                      ↑
              Ничто не зависит от routes
              Domain не зависит ни от чего внешнего
```

---

## Внутренняя структура Rust сервиса

```
services/rs/{service}/
├── src/
│   ├── main.rs          # Точка входа, wiring
│   ├── config.rs        # Конфигурация из env
│   ├── routes/          # HTTP/gRPC handlers
│   ├── services/        # Бизнес-логика
│   └── adapters/        # Внешние зависимости (DB, Redis, S3)
├── tests/               # Integration tests
├── Cargo.toml
└── Dockerfile
```

---

## Внутренняя структура Frontend приложения

```
apps/{app}/
├── app/                   # Next.js App Router
│   ├── (group)/           #   Route groups (без влияния на URL)
│   │   ├── page.tsx       #     Server Component по умолчанию
│   │   ├── layout.tsx     #     Layout для группы
│   │   ├── loading.tsx    #     Streaming skeleton
│   │   └── error.tsx      #     Error boundary
│   ├── layout.tsx         #   Root layout
│   └── globals.css        #   Tailwind directives
├── components/            #   Компоненты специфичные для этого app
│   └──                    #     Используют packages/ui как основу
├── hooks/                 #   Custom React hooks
├── lib/                   #   API вызовы, утилиты, конфиг
├── public/                #   Статика (favicon, robots.txt)
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

**Правила:**
- `app/` — только page.tsx, layout.tsx, loading.tsx, error.tsx. Без бизнес-логики
- `components/` — UI специфичный для приложения. Общее — в `packages/ui/`
- `hooks/` — data fetching, form logic, local state. Не дублировать между apps — выносить в `packages/shared/`
- `lib/` — обертки над `packages/api-client/`, конфиг, auth helpers
- Server Components по умолчанию. `"use client"` только когда нужен interactivity

## Shared UI Kit (`packages/ui/`)

```
packages/ui/
├── components/
│   ├── button.tsx         # Каждый компонент — один файл
│   ├── input.tsx          # Экспорт через index.ts
│   ├── modal.tsx
│   ├── video-player.tsx
│   └── ...
├── tokens/
│   ├── colors.ts          # Design tokens как JS объекты
│   ├── spacing.ts
│   └── typography.ts
├── index.ts               # Public API пакета
├── tailwind.config.ts     # Shared Tailwind preset
├── tsconfig.json
└── package.json
```

**Правила:**
- Каждый компонент — самодостаточный, без внешних зависимостей кроме Radix и Tailwind
- Props типизированы, дефолты указаны, forwardRef где нужен DOM доступ
- Не содержит бизнес-логику. Только UI: рендер, стили, accessibility, анимации

---

## Принципы расширения

1. **Новый сервис** — создай директорию в `services/py/` или `services/rs/`, добавь proto контракт
2. **Новый event** — определи в `proto/events/v1/`, сгенерируй код, подпишись в нужном сервисе
3. **Shared код** — сначала скопируй. Если дублируется в 3+ местах — вынеси в `libs/`
4. **Новый worker** — пока живет внутри сервиса. Выделяй когда нужна независимая масштабируемость
5. **Новый frontend app** — создай директорию в `apps/`, переиспользуй `packages/ui/` и `packages/api-client/`
6. **Новый UI компонент** — если используется в 1 app → в `apps/{app}/components/`. Если в 2+ → в `packages/ui/`
