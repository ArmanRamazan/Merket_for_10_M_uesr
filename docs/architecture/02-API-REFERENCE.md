# 02 — API Reference

> Последнее обновление: 2026-02-20
> Стадия: MVP (Phase 0)

---

## Identity Service (`:8001`)

### POST /register

Регистрация нового пользователя. Роль по умолчанию — `student`.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secret123",
  "name": "Ivan Petrov",
  "role": "student"          // optional, default "student". Enum: "student" | "teacher"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**
| Code | Причина |
|------|---------|
| 409 | Email уже зарегистрирован |
| 422 | Невалидные данные (email формат, пустые поля) |

---

### POST /login

Аутентификация по email + password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**
| Code | Причина |
|------|---------|
| 400 | Неверный email или пароль |
| 422 | Невалидные данные |

---

### GET /me

Информация о текущем пользователе. Требует JWT.

**Headers:** `Authorization: Bearer <token>`

**Response `200`:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "Ivan Petrov",
  "role": "student",
  "is_verified": false,
  "created_at": "2026-02-20T12:00:00+00:00"
}
```

**Errors:**
| Code | Причина |
|------|---------|
| 401 | Отсутствует или невалидный токен |

---

## Course Service (`:8002`)

### GET /courses

Список курсов с пагинацией и поиском. Публичный endpoint, не требует авторизации.

**Query params:**
| Параметр | Тип | Default | Описание |
|----------|-----|---------|----------|
| `q` | string | — | Поиск по title/description (ILIKE) |
| `limit` | int (1-100) | 20 | Количество записей |
| `offset` | int (≥0) | 0 | Смещение |

**Response `200`:**
```json
{
  "items": [
    {
      "id": "...",
      "teacher_id": "...",
      "title": "Python для начинающих",
      "description": "Основы Python...",
      "is_free": true,
      "price": null,
      "duration_minutes": 120,
      "level": "beginner",
      "created_at": "2026-02-20T12:00:00+00:00"
    }
  ],
  "total": 42
}
```

---

### GET /courses/{course_id}

Детали одного курса. Публичный endpoint.

**Response `200`:** Объект `Course` (см. выше).

**Errors:**
| Code | Причина |
|------|---------|
| 404 | Курс не найден |

---

### POST /courses

Создание курса. Только для **verified teacher**.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "title": "Python для начинающих",
  "description": "Основы Python",
  "is_free": true,
  "price": null,
  "duration_minutes": 120,
  "level": "beginner"
}
```

**Response `201`:** Объект `Course`.

**Errors:**
| Code | Причина |
|------|---------|
| 401 | Отсутствует или невалидный токен |
| 403 | `role != teacher` — "Only teachers can create courses" |
| 403 | `is_verified == false` — "Only verified teachers can create courses" |
| 422 | Невалидные данные |

---

## Enrollment Service (`:8003`)

### POST /enrollments

Записаться на курс. Только для `role=student`.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "course_id": "550e8400-e29b-41d4-a716-446655440000",
  "payment_id": "660e8400-e29b-41d4-a716-446655440000"  // optional, для платных курсов
}
```

**Response `201`:**
```json
{
  "id": "...",
  "student_id": "...",
  "course_id": "...",
  "payment_id": null,
  "status": "enrolled",
  "enrolled_at": "2026-02-20T12:00:00+00:00"
}
```

**Errors:**
| Code | Причина |
|------|---------|
| 401 | Отсутствует или невалидный токен |
| 403 | `role != student` — "Only students can enroll in courses" |
| 409 | Уже записан на курс (UNIQUE constraint) |
| 422 | Невалидные данные |

---

### GET /enrollments/me

Мои записи на курсы. Требует JWT.

**Headers:** `Authorization: Bearer <token>`

**Query params:**
| Параметр | Тип | Default | Описание |
|----------|-----|---------|----------|
| `limit` | int (1-100) | 20 | Количество записей |
| `offset` | int (≥0) | 0 | Смещение |

**Response `200`:**
```json
{
  "items": [{ "id": "...", "student_id": "...", "course_id": "...", "payment_id": null, "status": "enrolled", "enrolled_at": "..." }],
  "total": 5
}
```

---

### GET /enrollments/course/{course_id}/count

Количество записей на курс. Публичный endpoint.

**Response `200`:**
```json
{
  "course_id": "...",
  "count": 42
}
```

---

## Payment Service (`:8004`)

### POST /payments

Mock оплата курса. Всегда возвращает `status=completed`. Только для `role=student`.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "course_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 49.99
}
```

**Response `201`:**
```json
{
  "id": "...",
  "student_id": "...",
  "course_id": "...",
  "amount": "49.99",
  "status": "completed",
  "created_at": "2026-02-20T12:00:00+00:00"
}
```

**Errors:**
| Code | Причина |
|------|---------|
| 401 | Отсутствует или невалидный токен |
| 403 | `role != student` — "Only students can make payments" |
| 422 | Невалидные данные (amount <= 0) |

---

### GET /payments/{id}

Статус оплаты. Требует JWT.

**Headers:** `Authorization: Bearer <token>`

**Response `200`:** Объект `Payment`.

**Errors:**
| Code | Причина |
|------|---------|
| 404 | Оплата не найдена |

---

### GET /payments/me

Мои оплаты. Требует JWT.

**Headers:** `Authorization: Bearer <token>`

**Query params:** `limit`, `offset` (аналогично другим /me endpoints).

**Response `200`:**
```json
{
  "items": [{ "id": "...", "student_id": "...", "course_id": "...", "amount": "49.99", "status": "completed", "created_at": "..." }],
  "total": 3
}
```

---

## Notification Service (`:8005`)

### POST /notifications

Создать уведомление. Логирует `[NOTIFICATION]` в stdout. Требует JWT.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "type": "enrollment",
  "title": "Вы записались на курс: Python 101",
  "body": "Бесплатная запись"
}
```

**Response `201`:**
```json
{
  "id": "...",
  "user_id": "...",
  "type": "enrollment",
  "title": "...",
  "body": "...",
  "is_read": false,
  "created_at": "2026-02-20T12:00:00+00:00"
}
```

---

### GET /notifications/me

Мои уведомления. Требует JWT.

**Headers:** `Authorization: Bearer <token>`

**Query params:** `limit`, `offset`.

**Response `200`:**
```json
{
  "items": [{ "id": "...", "user_id": "...", "type": "enrollment", "title": "...", "body": "...", "is_read": false, "created_at": "..." }],
  "total": 10
}
```

---

### PATCH /notifications/{id}/read

Пометить уведомление как прочитанное. Требует JWT. Проверяет, что уведомление принадлежит текущему пользователю.

**Headers:** `Authorization: Bearer <token>`

**Response `200`:** Объект `Notification` с `is_read: true`.

**Errors:**
| Code | Причина |
|------|---------|
| 404 | Уведомление не найдено или не принадлежит пользователю |

---

## JWT Token Format

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "iat": 1740000000,
  "exp": 1740003600,
  "role": "teacher",
  "is_verified": true
}
```

| Claim | Тип | Описание |
|-------|-----|----------|
| `sub` | UUID string | User ID |
| `iat` | int | Issued at (unix timestamp) |
| `exp` | int | Expiration (iat + 3600 сек) |
| `role` | string | `"student"` или `"teacher"` |
| `is_verified` | bool | Верифицирован ли преподаватель |

- Алгоритм: **HS256**
- Shared secret: `JWT_SECRET` env var (одинаковый для всех сервисов)
- TTL: 1 час (3600 секунд)
- Оба сервиса валидируют JWT самостоятельно, без обращения к Identity

---

## Frontend Proxy (Next.js Rewrites)

Фронтенд проксирует запросы к API через Next.js rewrites:

| Frontend path | Backend destination |
|---------------|-------------------|
| `/api/identity/*` | `http://localhost:8001/*` |
| `/api/course/*` | `http://localhost:8002/*` |
| `/api/enrollment/*` | `http://localhost:8003/*` |
| `/api/payment/*` | `http://localhost:8004/*` |
| `/api/notification/*` | `http://localhost:8005/*` |

---

## Error Response Format

Все ошибки возвращаются в едином формате:

```json
{
  "detail": "Описание ошибки"
}
```
