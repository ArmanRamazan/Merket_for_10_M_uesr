from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    database_url: str
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_ttl_seconds: int = 3600
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"
    rate_limit_per_minute: int = 100
