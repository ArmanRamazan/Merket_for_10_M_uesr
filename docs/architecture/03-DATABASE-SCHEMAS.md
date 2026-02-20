# 03 — Database Schemas

> Последнее обновление: 2026-02-21
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
       ├── table: courses
       ├── table: modules
       ├── table: lessons
       └── table: reviews

enrollment-db (PostgreSQL 16 Alpine, :5435)
  └── database: enrollment
       ├── table: enrollments
       └── table: lesson_progress

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
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin');
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
| `role` | user_role | NOT NULL, DEFAULT 'student' | Роль: student, teacher или admin |
| `is_verified` | BOOLEAN | NOT NULL, DEFAULT false | Верификация преподавателя |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата создания |

**Индексы:** только PK (id) и UNIQUE (email). Намеренно нет дополнительных индексов — bottleneck для load testing.

**Миграции:**
- `001_users.sql` — создание таблицы users
- `002_add_role.sql` — добавление role ENUM и is_verified
- `003_add_admin_role.sql` — добавление значения `admin` в ENUM user_role

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
    avg_rating       NUMERIC(3,2),
    review_count     INTEGER NOT NULL DEFAULT 0,
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
| `avg_rating` | NUMERIC(3,2) | nullable | Средний рейтинг (денормализация) |
| `review_count` | INTEGER | NOT NULL, DEFAULT 0 | Количество отзывов (денормализация) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Дата создания |

**Индексы:** только PK (id). `teacher_id` не имеет FK constraint — eventual consistency.

**Поиск:** `ILIKE '%query%'` по title и description — намеренно без индекса (bottleneck для load testing). При search p99 > 300ms → добавить GIN/trigram index.

**Миграции:**
- `001_courses.sql` — создание ENUM course_level и таблицы courses
- `002_modules_lessons.sql` — таблицы modules и lessons
- `003_reviews.sql` — таблица reviews + avg_rating/review_count в courses

### Table: `modules`

```sql
CREATE TABLE modules (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id  UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title      VARCHAR(500) NOT NULL,
    "order"    INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Table: `lessons`

```sql
CREATE TABLE lessons (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id        UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title            VARCHAR(500) NOT NULL,
    content          TEXT NOT NULL DEFAULT '',
    video_url        VARCHAR(2000),
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    "order"          INTEGER NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Table: `reviews`

```sql
CREATE TABLE reviews (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    course_id  UUID NOT NULL,
    rating     SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment    TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(student_id, course_id)
);
```

**Денормализация:** `courses.avg_rating` (NUMERIC(3,2)) и `courses.review_count` (INTEGER) обновляются при создании review.

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
- `002_lesson_progress.sql` — таблица lesson_progress

### Table: `lesson_progress`

```sql
CREATE TABLE lesson_progress (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id   UUID NOT NULL,
    lesson_id    UUID NOT NULL,
    course_id    UUID NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(student_id, lesson_id)
);
```

| Column | Type | Constraints | Описание |
|--------|------|-------------|----------|
| `id` | UUID | PK, auto | Уникальный идентификатор |
| `student_id` | UUID | NOT NULL | ID студента |
| `lesson_id` | UUID | NOT NULL | ID урока (из Course Service) |
| `course_id` | UUID | NOT NULL | ID курса (для быстрого подсчёта прогресса) |
| `completed_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Когда урок завершён |

**Индексы:** PK (id) + UNIQUE (student_id, lesson_id).

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
