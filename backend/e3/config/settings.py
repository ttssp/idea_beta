
"""
Application Settings
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # API
    api_title: str = "E3: Integration & Action API"
    api_version: str = "v1"
    api_prefix: str = "/api/v1"

    # 数据库
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/e3"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # 幂等控制
    idempotency_ttl_hours: int = 24

    # 重试策略
    max_retries: int = 5
    retry_base_delay_seconds: int = 60

    # 熔断器
    circuit_breaker_fail_max: int = 5
    circuit_breaker_reset_timeout_seconds: int = 30

    # OAuth
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None

    # Webhook
    webhook_secret: str = "dev-secret-change-in-production"

    # 监控
    enable_prometheus: bool = True

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_prefix = "E3_"
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()

