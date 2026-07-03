from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.infrastructure.db import async_session
from src.shared.infrastructure.middlewares.policy.policy_registry import get_user_reader


class UserContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware for setting user context in the request state
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        """
        1. Extract the user ID from the request state (set by the AuthMiddleware).
        2. If a user ID is present, retrieve the user session data using the UserReader and set it in the request state for downstream handlers to access.
        """
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            # Fresh DB session per request; AsyncSession is not concurrency safe.
            async with async_session() as db_session:
                user_reader = get_user_reader(db_session)
                user = await user_reader.get_user(user_id)
            request.state.user = user

        response = await call_next(request)
        return response
