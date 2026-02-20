# 08 — Монорепа и Developer Experience

> Владелец: Principal Developer / Platform Team
> Последнее обновление: 2026-02-20

---

## Целевая структура монорепы

```
eduplatform/
├── CLAUDE.md                    # AI-assistant instructions
├── README.md
├── Cargo.toml                   # Rust workspace root
├── pyproject.toml               # Python workspace root (uv)
├── justfile                     # Task runner (just)
│
├── proto/                       # Shared protobuf definitions
│   ├── course/v1/
│   ├── enrollment/v1/
│   ├── payments/v1/
│   └── events/v1/
│
├── libs/                        # Shared libraries
│   ├── py/
│   │   ├── common/              # Python shared: logging, errors, config
│   │   ├── db/                  # Database utilities, migrations
│   │   └── testing/             # Test fixtures, factories
│   └── rs/
│       ├── common/              # Rust shared: error types, config
│       ├── proto-gen/           # Generated protobuf code
│       └── testing/             # Rust test utilities
│
├── services/                    # Deployable services
│   ├── py/
│   │   ├── identity/            # Auth, users, roles (student/teacher)
│   │   ├── course/              # Courses, lessons, materials
│   │   ├── enrollment/          # Enrollment, progress, certificates
│   │   ├── notifications/       # Email, push, SMS
│   │   ├── moderation/          # Content moderation
│   │   ├── teacher-tools/       # Teacher dashboard backend
│   │   └── analytics-api/       # Analytics API
│   └── rs/
│       ├── search/              # Search engine proxy + ranking
│       ├── video-processor/     # Transcoding, streaming
│       ├── messaging/           # WebSocket real-time Q&A
│       ├── payment-engine/      # Transaction processing
│       ├── event-ingestion/     # High-throughput event collector
│       └── api-gateway/         # Gateway, rate limiting, routing
│
├── workers/                     # Background workers
│   ├── py/
│   │   ├── email-sender/
│   │   ├── certificate-generator/
│   │   └── analytics-aggregator/
│   └── rs/
│       ├── video-transcoder/
│       └── feed-builder/
│
├── migrations/                  # Database migrations (per service)
│   ├── identity/
│   ├── course/
│   ├── enrollment/
│   └── payments/
│
├── deploy/                      # Infrastructure as Code
│   ├── k8s/                     # Kubernetes manifests
│   ├── terraform/               # Cloud infrastructure
│   └── docker/                  # Dockerfiles
│
├── docs/                        # Documentation
│   ├── goals/                   # ← Эти файлы
│   ├── architecture/            # C4 diagrams, ADRs
│   └── phases/                  # Phase plans
│
└── tools/                       # Developer tools
    ├── cli/                     # Internal CLI (Rust)
    ├── seed/                    # Database seeding scripts
    └── locust/                  # Load test scenarios
```

---

## TODO: Developer Experience

### Build и CI
- [ ] 🔴 Выбрать monorepo build tool: Pants / Bazel / Turborepo+Cargo — benchmark каждый
- [ ] 🔴 Selective CI: запускать тесты только для измененных сервисов и их зависимостей
- [ ] 🔴 Parallel builds: Python и Rust собираются параллельно
- [ ] 🔴 Docker build optimization: multi-stage builds, layer caching, < 60 сек на сервис
- [ ] 🔴 CI time budget: full pipeline < 10 минут, PR checks < 5 минут

### Local Development
- [ ] 🔴 `just dev` — поднять все нужные сервисы локально за 1 команду
- [ ] 🔴 Docker Compose для зависимостей (PostgreSQL, Redis, NATS, Meilisearch)
- [ ] 🔴 Hot reload для Python сервисов
- [ ] 🔴 Watch mode для Rust сервисов (cargo-watch)
- [ ] 🔴 Database seeding: `just seed` — заполнить БД тестовыми данными
- [ ] 🔴 Документация: "Getting started" за < 15 минут для нового разработчика

### Code Quality
- [ ] 🔴 Python: ruff (lint + format), mypy (strict), pytest
- [ ] 🔴 Rust: clippy (strict), rustfmt, cargo test
- [ ] 🔴 Pre-commit hooks: format, lint, type-check (только changed files)
- [ ] 🔴 CODEOWNERS: каждый сервис имеет явного владельца
- [ ] 🔴 Architectural tests: проверка что domain не импортирует infrastructure

### Протоколы и контракты
- [ ] 🔴 Protobuf как single source of truth для межсервисных контрактов
- [ ] 🔴 Автогенерация Python и Rust кода из .proto файлов
- [ ] 🔴 Breaking change detection в CI (buf breaking)
- [ ] 🔴 OpenAPI spec для публичного REST API (автогенерация из FastAPI)

### Testing стратегия
- [ ] 🔴 Unit tests: каждый сервис, мокают внешние зависимости, < 30 сек
- [ ] 🔴 Integration tests: сервис + его БД (testcontainers), < 2 мин
- [ ] 🔴 Contract tests: проверка совместимости между сервисами (Pact)
- [ ] 🔴 E2E tests: критические бизнес-потоки (регистрация → запись на курс → прохождение), < 5 мин
- [ ] 🔴 Load tests: Locust сценарии, запуск еженедельно
- [ ] 🔴 Chaos tests: ежемесячно в staging
