from typing import Any
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config.settings import config
from src.shared.infrastructure.context.request_context import request_id_ctx


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to set request id, client ip, and parsed user-agent
    (device + browser) on request state.
    """

    async def dispatch(self, request, call_next):
        """
        1. Get the request ID from the incoming request headers or generate a new one if not present.
        2. Store the request ID in the request state for potential use in route handlers.
        """
        request_id = request.headers.get("x-request-id") or str(uuid4())
        ip_address = self._get_client_ip(request)

        user_agent = self._get_user_agent(request)
        ua = self._parse_user_agent(user_agent)
        device = ua.get("device", ("unknown",))
        browser = ua.get("browser", ("unknown",))

        request.state.request_id = request_id
        request.state.ip_address = ip_address
        request.state.user_agent = user_agent
        request.state.device = device[0]
        request.state.browser = browser[0]

        # Expose to deep-layer code (e.g. the audit writer) via ContextVar.
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers["x-request-id"] = request_id
        return response

    def _get_client_ip(self, request) -> str:
        """
        Retrieves the client's IP address from the request headers or connection information.
        """
        # Only trust forwarding headers when explicitly running behind a trusted
        # reverse proxy; otherwise a client could spoof its source IP (which is
        # persisted to the audit log).
        if config.TRUST_PROXY_HEADERS:
            x_forwarded_for = request.headers.get("X-Forwarded-For")
            if x_forwarded_for:
                return x_forwarded_for.split(",")[0].strip()
        if request.client is None:
            return "unknown"
        return request.client.host

    def _get_user_agent(self, request) -> str:
        """
        Retrieves the client's User-Agent string from the request headers.
        """
        return request.headers.get("User-Agent", "unknown")

    def _parse_user_agent(self, user_agent: str) -> dict[str, Any]:
        """
        Parse the user-agent string to determine the device type and browser name.
        """
        import user_agents

        ua = user_agents.parse(user_agent)
        browser = (f"{ua.browser.family} {ua.browser.version_string}",)
        device = (f"{ua.device.family}",)

        return {
            "device": device,
            "browser": browser,
        }
