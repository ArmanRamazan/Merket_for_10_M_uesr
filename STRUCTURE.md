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
| Отдельный `frontend/` | Зависит от решения | Frontend может быть в этой репе или отдельной — решить на Phase 0 |

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

## Принципы расширения

1. **Новый сервис** — создай директорию в `services/py/` или `services/rs/`, добавь proto контракт
2. **Новый event** — определи в `proto/events/v1/`, сгенерируй код, подпишись в нужном сервисе
3. **Shared код** — сначала скопируй. Если дублируется в 3+ местах — вынеси в `libs/`
4. **Новый worker** — пока живет внутри сервиса. Выделяй когда нужна независимая масштабируемость
