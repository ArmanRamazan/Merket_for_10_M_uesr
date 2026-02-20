# 03 — Database Schemas

> Последнее обновление: 2026-02-20
> Стадия: MVP (Phase 0)

---

## Принцип: Database-per-Service

Каждый сервис владеет собственной PostgreSQL базой. Прямой доступ к БД другого сервиса запрещён.

```
identity-db (PostgreSQL 16 Alpine, :5433)
  └── database: identity
       └── table: users

course-db (PostgreSQL 16 Alpine, :5434)
  └── database: course
       └── table: courses

enrollment-db (PostgreSQL 16 Alpine, :5435)
  └── database: enrollment
       └── table: enrollments

payment-db (PostgreSQL 16 Alpine, :5436)
  └── database: payment
       └── table: payments

notification-db (PostgreSQL 16 Alpine, :5437)
  └── database: notification
       └── table: notifications
```

---

## Identity DB

### ENUM: `user_role`

```sql
CREATE TYPE user_role AS ENUM ('student', 'teacher');
```

### Table: `users`

```sql
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name          VARCHAR(255) NOT NULL,
    role          user_role NOT NULL DEFAULT 'student',
    is_verified   BOOLEAN NOT NULL DEFAULT false,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

| Column | Type | Constraints | Описание |
|--------|------|-------------|----------|
| `id` | UUID | PK, auto | Уникальный идентификатор |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Email для входа |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt hash пароля |
| `name` | VARCHAR(255) | NOT NULL | Имя пользователя |
| `role` | user_role | NOT NULL, DEFAULT 'student' | Роль: student или teacher |
| `is_verified` | BOOLEAN | NOT NULL, DEFAULT false | Верификация преподавателя |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата создания |

**Индексы:** только PK (id) и UNIQUE (email). Намеренно нет дополнительных индексов — bottleneck для load testing.

**Миграции:**
- `001_users.sql` — создание таблицы users
- `002_add_role.sql` — добавление role ENUM и is_verified

---

## Course DB

### ENUM: `course_level`

```sql
CREATE TYPE course_level AS ENUM ('beginner', 'intermediate', 'advanced');
```

### Table: `courses`

```sql
CREATE TABLE courses (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id       UUID NOT NULL,
    title            VARCHAR(500) NOT NULL,
    description      TEXT NOT NULL DEFAULT '',
    is_free          BOOLEAN NOT NULL DEFAULT true,
    price            NUMERIC(12,2),
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    level            course_level NOT NULL DEFAULT 'beginner',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

| Column | Type | Constraints | Описание |
|--------|------|-------------|----------|
| `id` | UUID | PK, auto | Уникальный идентификатор |
| `teacher_id` | UUID | NOT NULL | ID преподавателя (из Identity) |
| `title` | VARCHAR(500) | NOT NULL | Название курса |
| `description` | TEXT | NOT NULL, DEFAULT '' | Описание курса |
| `is_free` | BOOLEAN | NOT NULL, DEFAULT true | Бесплатный курс |
| `price` | NUMERIC(12,2) | nullable | Цена (если не бесплатный) |
| `duration_minutes` | INTEGER | NOT NULL, DEFAULT 0 | Длительность в минутах |
| `level` | course_level | NOT NULL, DEFAULT 'beginner' | Уровень сложности |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата создания |

**Индексы:** только PK (id). `teacher_id` не имеет FK constraint — eventual consistency.

**Поиск:** `ILIKE '%query%'` по title и description — намеренно без индекса (bottleneck для load testing). При search p99 > 300ms → добавить GIN/trigram index.

**Миграции:**
- `001_courses.sql` — создание ENUM course_level и таблицы courses

---

## Enrollment DB

### ENUM: `enrollment_status`

```sql
CREATE TYPE enrollment_status AS ENUM ('enrolled', 'in_progress', 'completed');
```

### Table: `enrollments`

```sql
CREATE TABLE enrollments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  UUID NOT NULL,
    course_id   UUID NOT NULL,
    payment_id  UUID,
    status      enrollment_status NOT NULL DEFAULT 'enrolled',
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(student_id, course_id)
);
```

| Column | Type | Constraints | Описание |
|--------|------|-------------|----------|
| `id` | UUID | PK, auto | Уникальный идентификатор |
| `student_id` | UUID | NOT NULL | ID студента (из Identity) |
| `course_id` | UUID | NOT NULL | ID курса (из Course) |
| `payment_id` | UUID | nullable | ID оплаты (из Payment, для платных курсов) |
| `status` | enrollment_status | NOT NULL, DEFAULT 'enrolled' | Статус записи |
| `enrolled_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата записи |

**Индексы:** PK (id) + UNIQUE (student_id, course_id). Нет FK constraints — eventual consistency.

**Миграции:**
- `001_enrollments.sql` — создание ENUM enrollment_status и таблицы enrollments

---

## Payment DB

### ENUM: `payment_status`

```sql
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'refunded');
```

### Table: `payments`

```sql
CREATE TABLE payments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  UUID NOT NULL,
    course_id   UUID NOT NULL,
    amount      NUMERIC(12,2) NOT NULL,
    status      payment_status NOT NULL DEFAULT 'completed',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

| Column | Type | Constraints | Описание |
|--------|------|-------------|----------|
| `id` | UUID | PK, auto | Уникальный идентификатор |
| `student_id` | UUID | NOT NULL | ID студента |
| `course_id` | UUID | NOT NULL | ID курса |
| `amount` | NUMERIC(12,2) | NOT NULL | Сумма оплаты |
| `status` | payment_status | NOT NULL, DEFAULT 'completed' | Статус (MVP: всегда completed) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата оплаты |

**Миграции:**
- `001_payments.sql` — создание ENUM payment_status и таблицы payments

---

## Notification DB

### ENUM: `notification_type`

```sql
CREATE TYPE notification_type AS ENUM ('registration', 'enrollment', 'payment');
```

### Table: `notifications`

```sql
CREATE TABLE notifications (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL,
    type       notification_type NOT NULL,
    title      VARCHAR(500) NOT NULL,
    body       TEXT NOT NULL DEFAULT '',
    is_read    BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

| Column | Type | Constraints | Описание |
|--------|------|-------------|----------|
| `id` | UUID | PK, auto | Уникальный идентификатор |
| `user_id` | UUID | NOT NULL | ID пользователя |
| `type` | notification_type | NOT NULL | Тип уведомления |
| `title` | VARCHAR(500) | NOT NULL | Заголовок |
| `body` | TEXT | NOT NULL, DEFAULT '' | Тело уведомления |
| `is_read` | BOOLEAN | NOT NULL, DEFAULT false | Прочитано |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата создания |

**MVP:** Нет реальной отправки email. Уведомления хранятся в БД + лог в stdout.

**Миграции:**
- `001_notifications.sql` — создание ENUM notification_type и таблицы notifications

---

## Connection Pool

Все сервисы используют `asyncpg.Pool`:
- `min_size = 5`
- `max_size = 5`

Намеренно маленький пул — bottleneck для load testing. При pool exhaustion в логах → увеличить.

---

## Миграции

Forward-only SQL файлы. Запускаются автоматически при старте сервиса в `app/main.py` через `lifespan`:

```python
async with create_pool(settings.database_url) as pool:
    for sql_file in sorted(Path("migrations").glob("*.sql")):
        await pool.execute(sql_file.read_text())
```

Каждая миграция идемпотентна (`IF NOT EXISTS`, `IF NOT EXISTS`).
