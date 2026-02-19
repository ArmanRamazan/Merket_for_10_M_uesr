from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_ttl_seconds: int = 3600
