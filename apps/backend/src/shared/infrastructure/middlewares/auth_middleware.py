from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from src.core.utils.response import CustomResponse as cr
from src.shared.exceptions.base_exceptions import DomainError
from src.shared.exceptions.exception_handler import DOMAIN_TO_HTTP
from src.shared.infrastructure.context.request_context import actor_id_ctx
from src.shared.infrastructure.logger import logger


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Placeholder middleware for authentication and authorization.
    TODO: Integrate session validation, cookie parsing, cache checking and user details binding.
    """

    async def dispatch(self, request, call_next):
        # Allow OPTIONS requests and health check bypass
        if request.method in ["OPTIONS"] or request.url.path in ["/health", "/api/v1/health"]:
            return await call_next(request)

        try:
            # TODO: Extract session cookie / token
            session_uuid = request.cookies.get("session_uuid")
            
            # For scaffolding, we do not reject requests yet but print a warning/TODO.
            # Once user entity is implemented, raise UnAuthorizedError if session_uuid is missing.
            
            # Placeholder user_id
            user_id = None
            if session_uuid:
                # TODO: Retrieve user session from AuthContainer use case
                # user_session = await get_auth_container(db_session).get_user_session_usecase().execute(session_uuid)
                # if not user_session:
                #     raise UnAuthorizedError("Session expired")
                # user_id = user_session.user_id
                pass
            
            request.state.session_uuid = session_uuid
            request.state.user_id = user_id

            # Expose the actor to deep-layer code (e.g. context variables)
            if user_id:
                token = actor_id_ctx.set(user_id)
                try:
                    return await call_next(request)
                finally:
                    actor_id_ctx.reset(token)
            else:
                return await call_next(request)

        except DomainError as exc:
            status_code = DOMAIN_TO_HTTP.get(exc.code, HTTP_400_BAD_REQUEST)
            detail = getattr(exc, "error", str(exc))
            data = getattr(exc, "errors", None)
            return cr.error(status_code=status_code, error=detail, errors=data)
        except Exception as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            detail = "Error in auth middleware"
            logger.exception(f"Unexpected error in AuthMiddleware: {str(e)}")
            return cr.error(status_code=status_code, error=detail, errors=detail)
