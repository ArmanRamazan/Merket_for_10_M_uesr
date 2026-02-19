from common.config import BaseAppSettings


class Settings(BaseAppSettings):
    jwt_ttl_seconds: int = 3600
