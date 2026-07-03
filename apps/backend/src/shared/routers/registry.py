from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, File, UploadFile
from starlette.status import HTTP_201_CREATED

from src.core.utils.response import (
    CustomErrorResponseSchema,
    CustomSuccessResponseSchema,
)
from src.core.utils.response import CustomResponse as cr
## Modules routers ##
from src.modules.auth.presentation.routers.auth_routers_registry import (
    router as auth_router,
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

