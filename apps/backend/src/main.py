import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.config.settings import config
from src.core.lifespan import lifespan
from src.shared.exceptions.exception_handler import add_exceptions_handler
from src.shared.infrastructure.middlewares.registry import register_middlewares
from src.shared.mediator.discover import auto_discover_listeners
from src.shared.routers.registry import register_routers

# Monkey-patch prometheus_fastapi_instrumentator.routing._get_route_name
# to handle route objects without a `path` attribute (e.g. _IncludedRouter).
import prometheus_fastapi_instrumentator.routing as _pfi_routing

_original_get_route_name = _pfi_routing._get_route_name


def _safe_get_route_name(scope, routes, route_name=None):
    try:
        return _original_get_route_name(scope, routes, route_name)
    except AttributeError:
        return None


_pfi_routing._get_route_name = _safe_get_route_name


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    app = FastAPI(title=config.PROJECT_NAME, lifespan=lifespan)

    auto_discover_listeners("src.modules")

    Instrumentator().instrument(app).expose(app)
    register_routers(app)
    register_middlewares(app)
    add_exceptions_handler(app)

    return app


def create_socket_app_factory():
    """
    Uvicorn factory to create the Socket.IO wrapped ASGI application.
    """
    from src.gateway.websocket.socket_manager import create_socket_app

    return create_socket_app()


if __name__ == "__main__":
    from src.gateway.websocket.socket_manager import create_socket_app

    socket_app = create_socket_app()
    uvicorn.run(app=socket_app, factory=False, host="0.0.0.0", port=8000, reload=True)
