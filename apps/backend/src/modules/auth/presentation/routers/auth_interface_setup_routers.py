from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.auth.application.usecases.interface_setup.interface_setup_usecase import (
    InterfaceSetupUseCase,
)
from src.modules.auth.auth_container import get_auth_container
from src.modules.auth.infrastructure.uow.auth_uow import AuthUOW
from src.modules.auth.presentation.schemas.auth_interface_setup_schemas import (
    InterfaceSetupRequestSchema,
)
from src.shared.dependencies.access_guard import require_access
from src.shared.infrastructure.db import get_async_session

protected_router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=True,
                email_verified=True,
                onboarded=True,
                organization_member=True,
            )
        )
    ]
)

router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@protected_router.put("/interface", response_model=CustomSuccessResponseSchema)
async def interface_setup(
    request: Request,
    body: InterfaceSetupRequestSchema,
    session: AsyncSessionDep,
):
    """
    Endpoint to update the interface setup for the authenticated user.
    """
    async with AuthUOW(session):
        auth_container = get_auth_container(session)
        interface_setup_usecase: InterfaceSetupUseCase = (
            auth_container.interface_setup_usecase()
        )
        await interface_setup_usecase.execute(
            payload=body, user_id=request.state.user_id
        )

    return cr.success(message="Interface setup updated successfully")


router.include_router(protected_router)
