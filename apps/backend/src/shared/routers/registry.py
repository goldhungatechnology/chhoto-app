from fastapi import APIRouter, FastAPI
from starlette.status import HTTP_200_OK

from src.core.utils.response import (
    CustomErrorResponseSchema,
    CustomSuccessResponseSchema,
)
from src.core.utils.response import CustomResponse as cr
from src.modules.auth.presentation.routers.auth_routers_registry import (
    router as auth_router,
)

main_router = APIRouter(
    prefix="/api/v1", responses={422: {"model": CustomErrorResponseSchema}}
)


@main_router.get(
    "/health",
    response_model=CustomSuccessResponseSchema[dict],
    tags=["System"],
)
async def health_check():
    """
    Health check endpoint returning system status.
    """
    return cr.success(
        data={"status": "healthy", "service": "chhoto-backend"},
        message="System is running smoothly",
        status_code=HTTP_200_OK,
    )


def register_routers(app: FastAPI):
    """
    Register all routers to the FastAPI application.
    """
    # Mount module routers
    main_router.include_router(auth_router, prefix="/auth")

    # Add health check to root level as well
    @app.get("/health", response_model=CustomSuccessResponseSchema[dict], tags=["System"])
    async def root_health():
        return cr.success(
            data={"status": "healthy"},
            message="System is running smoothly",
            status_code=HTTP_200_OK,
        )

    app.include_router(main_router)
