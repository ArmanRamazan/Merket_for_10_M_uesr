# 04 — Authentication Flow

> Последнее обновление: 2026-02-20
> Стадия: MVP (Phase 0)

---

## Обзор

Аутентификация реализована через **JWT с shared secret**. Оба сервиса (Identity и Course) используют один и тот же `JWT_SECRET` для создания и валидации токенов.

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

## Авторизация в Course Service

Course Service **не обращается к Identity Service**. Вся авторизация происходит через JWT claims:

1. Route layer извлекает `Authorization: Bearer <token>` из header
2. Декодирует JWT тем же `JWT_SECRET` (env var)
3. Извлекает claims: `user_id` (sub), `role`, `is_verified`
4. Передаёт claims в service layer

**Проверки для `POST /courses`:**
- `role != "teacher"` → 403 "Only teachers can create courses"
- `is_verified == false` → 403 "Only verified teachers can create courses"

**Публичные endpoints** (`GET /courses`, `GET /courses/{id}`) — не требуют авторизации.

---

## JWT Claims

| Claim | Source | Описание |
|-------|--------|----------|
| `sub` | `user.id` (UUID → string) | Идентификатор пользователя |
| `iat` | `datetime.now(UTC)` | Время выпуска токена |
| `exp` | `iat + 3600s` | Время истечения |
| `role` | `user.role` | `"student"` или `"teacher"` |
| `is_verified` | `user.is_verified` | Статус верификации |

---

## Верификация преподавателей

В MVP верификация выполняется вручную через SQL:

```sql
UPDATE users SET is_verified = true WHERE email = 'teacher@example.com';
```

После изменения `is_verified` в БД, преподаватель должен **перелогиниться**, чтобы получить новый JWT с `is_verified=true`.

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
| Shared secret (HS256) | Простота, 2 сервиса | Phase 2 (RSA/JWKS при >5 сервисов) |
| Manual verification | Нет admin panel | Phase 1 |
| localStorage | Простота | Cookie httpOnly при production |
