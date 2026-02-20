# 04 — Authentication Flow

> Последнее обновление: 2026-02-21
> Стадия: MVP (Phase 0)

---

## Обзор

Аутентификация реализована через **JWT с shared secret**. Все 5 сервисов используют один и тот же `JWT_SECRET` для валидации токенов. Identity создаёт токены при register/login, остальные сервисы только валидируют.

```
┌─────────┐        ┌──────────┐        ┌──────────┐
│ Browser │        │ Identity │        │  Course  │
│         │        │  :8001   │        │  :8002   │
└────┬────┘        └────┬─────┘        └────┬─────┘
     │                  │                   │
     │  POST /register  │                   │
     │  {email,pass,    │                   │
     │   name,role}     │                   │
     │─────────────────▶│                   │
     │                  │                   │
     │                  │ bcrypt hash       │
     │                  │ INSERT user       │
     │                  │ JWT encode        │
     │                  │  (sub, role,      │
     │                  │   is_verified)    │
     │                  │                   │
     │  {access_token}  │                   │
     │◀─────────────────│                   │
     │                  │                   │
     │  POST /courses   │                   │
     │  Authorization:  │                   │
     │  Bearer <token>  │                   │
     │──────────────────┼──────────────────▶│
     │                  │                   │
     │                  │    JWT decode     │
     │                  │    (same secret)  │
     │                  │    Extract:       │
     │                  │    - user_id      │
     │                  │    - role         │
     │                  │    - is_verified  │
     │                  │                   │
     │                  │    Check:         │
     │                  │    role=teacher?  │
     │                  │    is_verified?   │
     │                  │                   │
     │  {course}        │                   │
     │◀─────────────────┼───────────────────│
```

---

## Регистрация

1. Пользователь отправляет `POST /register` с email, password, name и опционально role
2. Identity Service:
   - Проверяет уникальность email (409 Conflict если занят)
   - Хэширует пароль через `bcrypt.hashpw()` с `bcrypt.gensalt()`
   - Сохраняет пользователя в БД с `role` и `is_verified=false`
   - Создаёт JWT с extra_claims: `{role, is_verified}`
3. Возвращает `{access_token, token_type: "bearer"}`

---

## Логин

1. Пользователь отправляет `POST /login` с email и password
2. Identity Service:
   - Ищет пользователя по email (400 если не найден)
   - Проверяет пароль через `bcrypt.checkpw()`
   - Создаёт JWT с **текущими** значениями role и is_verified из БД
3. Возвращает `{access_token, token_type: "bearer"}`

---

## Авторизация в сервисах

Все сервисы **не обращаются к Identity Service**. Вся авторизация происходит через JWT claims:

1. Route layer извлекает `Authorization: Bearer <token>` из header
2. Декодирует JWT тем же `JWT_SECRET` (env var)
3. Извлекает claims: `user_id` (sub), `role`, `is_verified`
4. Передаёт claims в service layer

### Identity Service

**Admin-only (role=admin):**
- `GET /admin/teachers/pending` — список unverified teachers
- `PATCH /admin/users/{id}/verify` — верификация teacher

### Course Service

**Teacher-only (role=teacher + is_verified + owner check):**
- `POST /courses` — создание курса
- `PUT /courses/{id}` — редактирование курса
- `POST /courses/{id}/modules`, `PUT /modules/{id}`, `DELETE /modules/{id}` — управление модулями
- `POST /modules/{id}/lessons`, `PUT /lessons/{id}`, `DELETE /lessons/{id}` — управление уроками

**Student-only (role=student):**
- `POST /reviews` — отзыв на курс

**Публичные** (без авторизации):
- `GET /courses`, `GET /courses/{id}`, `GET /courses/{id}/curriculum`
- `GET /lessons/{id}`, `GET /reviews/course/{id}`

### Enrollment Service

**Student-only (role=student):**
- `POST /enrollments` — запись на курс
- `POST /progress/lessons/{id}/complete` — отметка прогресса

**Authenticated (любая роль):**
- `GET /enrollments/me`, `GET /progress/courses/{id}`, `GET /progress/courses/{id}/lessons`

**Публичные:**
- `GET /enrollments/course/{id}/count`

### Payment Service

**Student-only:** `POST /payments`
**Authenticated:** `GET /payments/{id}`, `GET /payments/me`

### Notification Service

**Authenticated:** `POST /notifications`, `GET /notifications/me`, `PATCH /notifications/{id}/read`

---

## JWT Claims

| Claim | Source | Описание |
|-------|--------|----------|
| `sub` | `user.id` (UUID → string) | Идентификатор пользователя |
| `iat` | `datetime.now(UTC)` | Время выпуска токена |
| `exp` | `iat + 3600s` | Время истечения |
| `role` | `user.role` | `"student"`, `"teacher"` или `"admin"` |
| `is_verified` | `user.is_verified` | Статус верификации |

---

## Верификация преподавателей

Верификация выполняется через Admin API:

1. Преподаватель регистрируется с `role=teacher` → получает `is_verified=false`
2. Администратор (`role=admin`) открывает панель `/admin/teachers` → видит список unverified teachers
3. Администратор нажимает "Одобрить" → `PATCH /admin/users/{id}/verify`
4. Identity Service обновляет `is_verified=true` в БД
5. Преподаватель **перелогинивается** → получает новый JWT с `is_verified=true` → может создавать курсы

**Admin endpoints (Identity Service):**
- `GET /admin/teachers/pending` — список unverified teachers (admin only)
- `PATCH /admin/users/{user_id}/verify` — верифицировать teacher (admin only)

**Seed admin:** `admin@eduplatform.com` / `password123` (создаётся в seed скрипте)

---

## Хранение токена на клиенте

Фронтенд хранит токен в `localStorage`:
- `token` — JWT access token
- `user` — JSON объект текущего пользователя (кэш)

При logout — оба ключа удаляются.

---

## Ограничения MVP

| Ограничение | Причина | Когда появится |
|-------------|---------|---------------|
| Нет refresh token | YAGNI для MVP | Phase 1 |
| Нет blacklist токенов | Нет Redis кэша | Phase 1 |
| Shared secret (HS256) | Простота, 5 сервисов | Phase 2 (RSA/JWKS при gateway) |
| ~~Manual verification~~ | ~~Нет admin panel~~ | ✅ Admin panel реализован |
| localStorage | Простота | Cookie httpOnly при production |
