from datetime import datetime, timedelta, timezone

import jwt


def create_access_token(
    user_id: str,
    secret: str,
    algorithm: str = "HS256",
    ttl_seconds: int = 3600,
    extra_claims: dict | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=ttl_seconds),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_token(token: str, secret: str, algorithm: str = "HS256") -> dict:
    return jwt.decode(token, secret, algorithms=[algorithm])
