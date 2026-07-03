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
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.SECRET_KEY,
        same_site="none",
        https_only=config.APP_URL.startswith("https"),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
