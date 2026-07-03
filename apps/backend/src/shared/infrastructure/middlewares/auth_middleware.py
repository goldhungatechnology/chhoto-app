from src.core.utils.response import CustomResponse as cr
from src.shared.exceptions.exception_handler import DOMAIN_TO_HTTP
from starlette.middleware.base import BaseHTTPMiddleware
from src.shared.exceptions.base_exceptions import (
    DomainError,
    UnAuthorizedError,
)

from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from src.modules.auth.auth_container import get_auth_container
from src.shared.infrastructure.middlewares.policy.public_path import is_public_path
from src.shared.infrastructure.logger import logger
from src.shared.infrastructure.db import async_session
from src.shared.infrastructure.context.request_context import actor_id_ctx
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for authentication and authorization.
    """

    def __init__(self, app):
        super().__init__(app)
        self.cache_service = AuthCacheService()

    async def dispatch(self, request, call_next):
        """
        1. Extract the  session uuid from the request headers.
        """
        if request.method in ["OPTIONS"] or is_public_path(
            request.url.path, request.method
        ):
            return await call_next(request)

        try:
            session_uuid = self._extract_session_uuid(request)
            if not session_uuid:
                raise UnAuthorizedError(
                    errors={"code": "UNAUTHENTICATED"},
                    error="Authentication credentials were not provided.Cookies must include a session_uuid.",
                )

            # A fresh DB session per request: AsyncSession is not concurrency
            # safe and must never be shared across requests.
            async with async_session() as db_session:
                auth_container = get_auth_container(db_session)
                usecase = auth_container.get_user_session_usecase()
                user_session = await usecase.execute(session_uuid)

            if not user_session:
                raise UnAuthorizedError(
                    errors={"code": "SESSION_EXPIRED"},
                    error="The session has expired or is invalid. Please log in again.",
                )

            request.state.session_uuid = user_session.uuid
            request.state.user_id = user_session.user_id

            await self.cache_service.set_user_last_seen(user_session.user_id)

            # Expose the actor to deep-layer code (e.g. the audit writer).
            token = actor_id_ctx.set(user_session.user_id)
            try:
                return await call_next(request)
            finally:
                actor_id_ctx.reset(token)
        except DomainError as exc:
            status_code = DOMAIN_TO_HTTP.get(exc.code, HTTP_400_BAD_REQUEST)
            detail = getattr(exc, "error", str(exc))
            data = getattr(exc, "errors", None)
            return cr.error(status_code=status_code, error=detail, errors=data)
        except Exception as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            detail = "Error in middleware"
            data = "Error in middleware"
            logger.exception(f"Unexpected error in AuthMiddleware {str(e)}")
            return cr.error(status_code=status_code, error=detail, errors=data)

    def _extract_session_uuid(self, request) -> str | None:
        """
        Extracts the session UUID from the request headers.
        """
        return request.cookies.get("session_uuid")
