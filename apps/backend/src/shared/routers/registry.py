from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, File, UploadFile
from starlette.status import HTTP_201_CREATED

from src.core.utils.response import (
    CustomErrorResponseSchema,
    CustomSuccessResponseSchema,
)
from src.core.utils.response import CustomResponse as cr
from src.modules.audit.presentation.routers.audit_routers_registry import (
    router as audit_router,
)

## Modules routers ##
from src.modules.auth.presentation.routers.auth_routers_registry import (
    router as auth_router,
)
from src.modules.organization.presentation.routers.organization_routers_registry import (
    router as organization_router,
)
from src.modules.visitor.presentation.routers.visitor_routers_registry import (
    router as visitor_router,
)
from src.modules.workforce.presentation.routers.workforce_routers_registry import (
    router as workforce_router,
)
from src.modules.motivation.presentation.routers.motivation_routers_registry import (
    router as motivation_router,
)

from src.shared.infrastructure.background_task_manager.routers import (
    router as background_task_router,
)
from src.shared.routers.country.country_router import public_router as country_router
from src.shared.infrastructure.uploader import uploader
from src.shared.schemas.file_schema import UploadedFileResponse

main_router = APIRouter(
    prefix="/api/v1", responses={422: {"model": CustomErrorResponseSchema}}
)


@main_router.post(
    "/files/upload",
    response_model=CustomSuccessResponseSchema[list[UploadedFileResponse]],
)
async def upload_files(files: Annotated[list[UploadFile], File(...)]):
    """
    upload files endpoint
    """
    payload: list[tuple[str, bytes, str | None]] = []
    for file in files:
        content = await file.read()
        payload.append((file.filename or "file", content, file.content_type))

    data: list[dict[str, Any]] = await uploader.upload_files(payload)
    return cr.success(
        data=[UploadedFileResponse(**item).model_dump() for item in data],
        message="Files uploaded successfully",
        status_code=HTTP_201_CREATED,
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
    from starlette.status import HTTP_200_OK
    return cr.success(
        data={"status": "healthy", "service": "chhoto-backend"},
        message="System is running smoothly",
        status_code=HTTP_200_OK,
    )


def register_routers(app: FastAPI):
    """
    Register all routers to the FastAPI application.
    """

    main_router.include_router(auth_router, prefix="/auth")
    main_router.include_router(organization_router, prefix="/organizations")
    main_router.include_router(motivation_router, prefix="/motivation")
    main_router.include_router(audit_router, prefix="/audit")
    main_router.include_router(workforce_router, prefix="/workforce")
    main_router.include_router(visitor_router, prefix="/visitors")
    main_router.include_router(background_task_router)
    main_router.include_router(country_router, prefix="/countries")
    
    @app.get("/health", response_model=CustomSuccessResponseSchema[dict], tags=["System"])
    async def root_health():
        from starlette.status import HTTP_200_OK
        return cr.success(
            data={"status": "healthy"},
            message="System is running smoothly",
            status_code=HTTP_200_OK,
        )

    app.include_router(main_router)

