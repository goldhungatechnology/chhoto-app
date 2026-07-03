import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.config.settings import config
from src.core.lifespan import lifespan
from src.shared.exceptions.exception_handler import add_exceptions_handler
from src.shared.infrastructure.middlewares.registry import register_middlewares
from src.shared.routers.registry import register_routers


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(title=config.PROJECT_NAME, lifespan=lifespan)

    # Instrument Prometheus metrics
    Instrumentator().instrument(app).expose(app)

    # Register application routes and global exception handlers
    register_routers(app)
    register_middlewares(app)
    add_exceptions_handler(app)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
