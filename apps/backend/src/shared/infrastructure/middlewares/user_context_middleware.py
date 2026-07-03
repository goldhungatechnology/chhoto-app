from starlette.middleware.base import BaseHTTPMiddleware


class UserContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware for setting detailed user context in the request state.
    TODO: Fetch the full user model using a user reader or cache and assign to request.state.user.
    """

    async def dispatch(self, request, call_next):
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            # TODO: Fetch user details from database or cache, e.g.:
            # async with async_session() as db_session:
            #     user = await get_user_reader(db_session).get_user(user_id)
            # request.state.user = user
            request.state.user = {"id": user_id, "role": "user"}  # Placeholder

        response = await call_next(request)
        return response
