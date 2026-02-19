from datetime import datetime, timedelta, timezone

import jwt


def create_access_token(
    user_id: str,
    secret: str,
    algorithm: str = "HS256",
    ttl_seconds: int = 3600,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=ttl_seconds),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_token(token: str, secret: str, algorithm: str = "HS256") -> dict:
    return jwt.decode(token, secret, algorithms=[algorithm])
