import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.core.config.settings import config
from src.shared.infrastructure.middlewares.auth_middleware import AuthMiddleware
from src.shared.infrastructure.middlewares.request_context_middleware import (
    RequestContextMiddleware,
)
from src.shared.infrastructure.middlewares.user_context_middleware import (
    UserContextMiddleware,
)


def register_middlewares(app: FastAPI):
    """
    register middlewares to the FastAPI app

    Execution order (top = first to run):
        1. CORSMiddleware
        2. RequestContextMiddleware
        3. AuthMiddleware
        4. UserContextMiddleware
    """
    app.add_middleware(UserContextMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RequestContextMiddleware)
    is_https = config.APP_URL.startswith("https")
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.SECRET_KEY,
        same_site="none" if is_https else "lax",
        https_only=is_https,
    )
    if config.is_staging:
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=rf"^https://([a-zA-Z0-9-]+\.)?{re.escape(config.ALLOWED_ORIGIN_DOMAIN)}$",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://auth.localhost:3000",
                "http://app.localhost:3000",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
