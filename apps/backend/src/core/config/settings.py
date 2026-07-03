import os
from enum import Enum, StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Final

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Load the base environment file if it exists
load_dotenv(BASE_DIR / "env" / ".env")


class Environment(StrEnum, Enum):
    """
    Environment Enum class
    """

    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    STAGING = "staging"
    TESTING = "testing"


environment = os.getenv("ENVIRONMENT", "development").lower()
env_file_path = {
    "local": "env/.env.local",
    "development": "env/.env.development",
    "production": "env/.env.production",
    "testing": "env/.env.test",
}

env_file = env_file_path.get(environment, "env/.env")
env_path = BASE_DIR / env_file


class Settings(BaseSettings):
    """
    Base settings class for entire application configuration
    """

    APP_URL: str = "http://localhost:8080"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    PROJECT_NAME: str = "chhoto-backend"
    SECRET_KEY: str = "your_default_secret_key"

    ## ---------------------------------------------- Database --------------------------------
    DATABASE_URL: str = "your_default_database_url"

    ## ---------------------------------------------- CORS & Frontend --------------------------------
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    TRUST_PROXY_HEADERS: bool = False

    ## ---------------------------------------------- GeoIP --------------------------------
    GEOIP_ENABLED: bool = False
    GEOIP_DB_PATH: str | None = None

    ## ---------------------------------------------- Caching --------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    ## ---------------------------------------------- Email & Notifications --------------------------------
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 2525
    SMTP_USERNAME: str = "your_smtp_username"
    SMTP_PASSWORD: str = "your_smtp_password"
    EMAIL_FROM: str = "noreply@example.com"

    ## -------------------------------- Authentication & Authorization --------------------------------
    TOKEN_DIGIT: int = 6
    ENABLE_CAPTCHA: bool = False
    COOKIE_DOMAIN: str = "mydomain"

    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 24
    USER_SESSION_EXPIRE_MINUTES: int = 60 * 24 * 7
    MAX_AUTH_CONCURRENT_SESSIONS: int = 5
    FORGOT_PASSWORD_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ONBOARDING_INVITATION_EXPIRE_HOURS: int = 168

    model_config = SettingsConfigDict(
        env_file=str(env_path), env_file_encoding="utf-8", frozen=True, extra="ignore"
    )

    @model_validator(mode="after")
    def _reject_insecure_defaults_in_production(self) -> "Settings":
        """
        Refuse to boot a production deployment with placeholder secrets.
        """
        if self.ENVIRONMENT == Environment.PRODUCTION:
            insecure = {
                "SECRET_KEY": "your_default_secret_key",
                "DATABASE_URL": "your_default_database_url",
                "COOKIE_DOMAIN": "mydomain",
            }
            offending = [
                name
                for name, default in insecure.items()
                if getattr(self, name) == default
            ]
            if offending:
                raise ValueError(
                    "Insecure default value(s) must be overridden via environment "
                    f"in {self.ENVIRONMENT}: {', '.join(offending)}"
                )
        return self

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        return self.ENVIRONMENT == Environment.STAGING

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == Environment.TESTING

    @property
    def is_local(self) -> bool:
        return self.ENVIRONMENT == Environment.LOCAL


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of the application settings."""
    return Settings()


config: Final[Settings] = get_settings()
