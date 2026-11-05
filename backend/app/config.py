"""Configuration settings using Pydantic Settings"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "SistemaTriaje"
    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "json"  # json | text

    # Database
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "soctriaje"
    db_user: str = "soc_app"
    db_password: str = Field(default="changeme", repr=False)

    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL URL"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = Field(default="", repr=False)
    redis_cache_ttl_virustotal: int = 86400  # 24 hours
    redis_cache_ttl_abuseipdb: int = 43200  # 12 hours
    redis_cache_ttl_geoip: int = 604800  # 7 days

    @property
    def redis_url(self) -> str:
        """Construct Redis URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    # JWT
    jwt_secret_key: str = Field(default="changeme_jwt_secret_key_min_32_chars", repr=False)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:80,http://localhost"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # API Keys
    service_api_key: str = Field(default="changeme_service_api_key", repr=False)

    # Rate Limiting
    rate_limit_per_minute_get: int = 100
    rate_limit_per_minute_post: int = 20

    # Security
    login_max_attempts: int = 5
    login_lockout_duration_minutes: int = 15
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_number: bool = True
    password_require_special: bool = False

    # Backend Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_workers: int = 4


# Singleton instance
settings = Settings()
