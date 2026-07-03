from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from src.core.utils.response import CustomResponse as cr
from src.shared.exceptions.base_exceptions import DomainError
from src.shared.infrastructure.logger import logger

DOMAIN_TO_HTTP = {
    "domain_error": HTTP_400_BAD_REQUEST,
    "not_found": HTTP_404_NOT_FOUND,
    "conflict_error": HTTP_409_CONFLICT,
    "create_error": HTTP_500_INTERNAL_SERVER_ERROR,
    "update_error": HTTP_500_INTERNAL_SERVER_ERROR,
    "invalid_error": HTTP_400_BAD_REQUEST,
    "server_error": HTTP_500_INTERNAL_SERVER_ERROR,
    "unauthorized_error": HTTP_401_UNAUTHORIZED,
    "forbidden_error": HTTP_403_FORBIDDEN,
}


async def global_exception_handler(request: Request, exc: Exception):
    """
    Handles the global exception with custom response
    """
    if isinstance(exc, RequestValidationError):
        status_code = HTTP_422_UNPROCESSABLE_CONTENT
        detail = "Validation Error"
        formatted = {}

        for error in exc.errors():
            path = ".".join(str(p) for p in error["loc"] if p != "body")
            message = error["msg"]
            formatted[path] = message

        data = formatted

    elif isinstance(exc, DomainError):
        status_code = DOMAIN_TO_HTTP.get(exc.code, HTTP_400_BAD_REQUEST)
        detail = getattr(exc, "error", str(exc))
        data = getattr(exc, "errors", None)
    else:
        logger.exception(
            "Unhandled exception while processing %s %s",
            request.method,
            request.url.path,
        )
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        detail = "Internal server error"
        data = None

    return cr.error(status_code=status_code, error=detail, errors=data)


def add_exceptions_handler(app: FastAPI):
    """
    Adds all exception handlers to the application
    """
    app.add_exception_handler(RequestValidationError, global_exception_handler)
    app.add_exception_handler(DomainError, global_exception_handler)
