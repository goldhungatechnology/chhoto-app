import os
from enum import Enum, StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Final

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

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
    "staging": "env/.env.staging",
    "production": "env/.env.production",
    "testing": "env/.env.test",
}

env_file = env_file_path.get(environment, "env/.env")
env_path = BASE_DIR / env_file


class Settings(BaseSettings):
    """
    base settings class for entire application configuration
    """

    APP_URL: str = "http://localhost:8080"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    PROJECT_NAME: str = "chatboq"
    SECRET_KEY: str = "your_default_secret_key"

    ## ---------------------------------------------- Database --------------------------------

    DATABASE_URL: str = "your_default_database_url"

    ## ---------------------------------------------- CORS & Frontend --------------------------------

    FRONTEND_URL: str = "http://localhost:3000"
    OAUTH_SUCCESS_REDIRECT_URL: str = f"{FRONTEND_URL}/dashboard"
    OAUTH_FAILURE_REDIRECT_URL: str = f"{FRONTEND_URL}/login?error=oauth_failed"
    # Origins allowed to make credentialed cross-origin requests. Defaults to
    # the configured frontend; override per-environment via env (comma/JSON list).
    CORS_ALLOWED_ORIGINS: list[str] = [FRONTEND_URL]
    # Only honor X-Forwarded-For / proxy headers when running behind a trusted
    # reverse proxy; otherwise clients could spoof their source IP.
    TRUST_PROXY_HEADERS: bool = False

    ## ---------------------------------------------- GeoIP --------------------------------
    # Path to the MaxMind GeoLite2-City .mmdb file. When the feature is disabled
    # or the file is missing, IP geolocation degrades gracefully to None.
    GEOIP_ENABLED: bool = False
    GEOIP_DB_PATH: str | None = None

    ## ---------------------------------------------- Caching --------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    ## ---------------------------------------------- Email & Notifications --------------------------------
    EMAIL_PROVIDER: str = "smtp"
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 2525
    SMTP_USERNAME: str = "your_smtp_username"
    SMTP_PASSWORD: str = "your_smtp_password"
    EMAIL_FROM: str = "noreply@example.com"
    RESEND_API_KEY: str | None = None

    ## ---------------------------------------------- File Storage --------------------------------

    ## ---- Cloudinary
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None
    CLOUDINARY_FOLDER: str = "ems"

    ## ---- AWS S3
    AWS_S3_BUCKET: str | None = None
    AWS_S3_REGION: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_S3_FOLDER: str = "ems"
    AWS_S3_ENDPOINT_URL: str | None = None
    AWS_S3_PUBLIC_BASE_URL: str | None = None

    ALLOWED_USER_EMAIL: str = ""

    ## -------------------------------- Authentication & Authorization --------------------------------
    ## ---- Core
    TEMP_EMAIL_DOMAINS: set[str] = {
        "tempmail.com",
        "10minutemail.com",
        "mailinator.com",
    }
    TOKEN_DIGIT: int = 6  # used by token service random token
    ENABLE_CAPTCHA: bool = True

    ## ---- Email
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 24

    ## ---- Session
    USER_SESSION_EXPIRE_MINUTES: int = 60 * 24 * 7
    MAX_AUTH_CONCURRENT_SESSIONS: int = 5

    ## ---- Password
    FORGOT_PASSWORD_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    ## ---- Onboarding
    ONBOARDING_INVITATION_EXPIRE_HOURS: int = 168

    ## OAuth
    GOOGLE_OAUTH_CLIENT_ID: str | None = None
    GOOGLE_OAUTH_CLIENT_SECRET: str | None = None

    ## --------------------------------  Background Task --------------------------------

    ## ---- outbox
    OUTBOX_POLLER_AUTOSTART: bool = True
    OUTBOX_POLLER_DELAY_INITIAL_SECONDS: int = 3
    # Must be >= INITIAL: the poller uses randint(INITIAL, MAX) for backoff.
    OUTBOX_POLLER_DELAY_MAX_SECONDS: int = 30

    ## ---------------------------------------------- Auditing --------------------------------
    AUDIT_ENABLED: bool = True
    AUDIT_STRICT_MODE: bool = False

    ## ---------------------------------------------- Captcha --------------------------------
    TURNSTILE_SECRET_KEY: str = "1x0000000000000000000000000000000AA"

    ## ---------------------------------------------- Cookies --------------------------------
    COOKIE_DOMAIN: str = "mydomain"

    model_config = SettingsConfigDict(
        env_file=str(env_path), env_file_encoding="utf-8", frozen=True, extra="ignore"
    )

    @model_validator(mode="after")
    def _reject_insecure_defaults_in_production(self) -> "Settings":
        """
        Refuse to boot a production deployment with placeholder secrets so the
        app can never run with a guessable JWT/session key or cookie domain.
        Non-production environments keep the convenient defaults.
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
        """Check if the current environment is production."""
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if the current environment is development."""
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        """Check if the current environment is staging."""
        return self.ENVIRONMENT == Environment.STAGING

    @property
    def is_testing(self) -> bool:
        """Check if the current environment is testing."""
        return self.ENVIRONMENT == Environment.TESTING

    @property
    def is_local(self) -> bool:
        """Check if the current environment is local."""
        return self.ENVIRONMENT == Environment.LOCAL

    def __str__(self) -> str:
        """Return string representation."""
        return f"Settings({self.model_dump()})"

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Settings({self.model_dump()})"


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of the application settings."""
    return Settings()


config: Final[Settings] = get_settings()
