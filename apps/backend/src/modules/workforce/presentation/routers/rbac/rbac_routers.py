from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.workforce.application.usecases.rbac.list_roles_usecase import (
    ListRolesUseCase,
)
from src.modules.workforce.application.usecases.rbac.list_permissions_usecase import (
    ListPermissionsUseCase,
)
from src.modules.workforce.infrastructure.uow.workforce_uow import WorkforceUOW
from src.modules.workforce.presentation.schemas.rbac.rbac_role_schemas import (
    CreateRoleRequestSchema,
    CreatedByUserSchema,
    PermissionResponseSchema,
    RoleResponseSchema,
)
from src.modules.workforce.workforce_container import get_workforce_container
from src.shared.dependencies.access_guard import require_access
from src.shared.dependencies.role_guard import require_org_role
from src.shared.infrastructure.db import get_async_session

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema

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

## main router
router = APIRouter()
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


## ------------------------------------------------ Protected Endpoints ------------------------------------------------ ##
@protected_router.get(
    "/roles", response_model=CustomSuccessResponseSchema[list[RoleResponseSchema]]
)
async def list_all_roles(request: Request, session: AsyncSessionDep):
    """
    Endpoint to list all roles in the system.
    """
    async with WorkforceUOW(session):
        workforce_container = get_workforce_container(
            session, request.state.organization_id
        )
        list_roles_usecase: ListRolesUseCase = workforce_container.list_roles_usecase()

        roles, users_map = await list_roles_usecase.execute()

        payload = []
        for role in roles:
            user = users_map.get(role.created_by_id)
            created_by = CreatedByUserSchema.model_validate(user) if user else None

            payload.append(
                RoleResponseSchema(
                    uuid=role.uuid,
                    name=role.name,
                    description=role.description,
                    created_by=created_by,
                    is_system_role=role.is_system_role,
                ).model_dump()
            )

        return cr.success(
            data=payload,
            message="Roles listed successfully",
        )


@protected_router.get(
    "/permissions",
    response_model=CustomSuccessResponseSchema[list[PermissionResponseSchema]],
)
async def list_all_permissions(request: Request, session: AsyncSessionDep):
    """
    Endpoint to list all permissions in the system.
    """
    async with WorkforceUOW(session):
        workforce_container = get_workforce_container(
            session, request.state.organization_id
        )
        list_permissions_usecase: ListPermissionsUseCase = (
            workforce_container.list_permissions_usecase()
        )

        permissions, users_map = await list_permissions_usecase.execute()

        payload = []
        for permission in permissions:
            user = users_map.get(permission.created_by_id)
            created_by = CreatedByUserSchema.model_validate(user) if user else None

            payload.append(
                PermissionResponseSchema(
                    uuid=permission.uuid,
                    name=permission.name,
                    key=permission.key,
                    description=permission.description,
                    category=permission.category,
                    created_by=created_by,
                    is_system_permission=permission.is_system_permission,
                ).model_dump()
            )

        return cr.success(
            data=payload,
            message="Permissions listed successfully",
        )


@protected_router.post(
    "/roles",
    response_model=CustomSuccessResponseSchema[RoleResponseSchema],
    dependencies=[Depends(require_org_role({"owner", "admin"}))],
)
async def create_role(
    request: Request, body: CreateRoleRequestSchema, session: AsyncSessionDep
):
    """
    Endpoint to create a new role in the system.
    """
    async with WorkforceUOW(session):
        workforce_container = get_workforce_container(
            session, request.state.organization_id
        )
        create_role_usecase = workforce_container.create_role_usecase()

        new_role = await create_role_usecase.execute(
            organization_id=request.state.organization_id,
            name=body.name,
            description=body.description,
            actor_id=request.state.user_id,
        )

        return cr.success(
            data=RoleResponseSchema.model_validate(new_role).model_dump(),
            message="Role created successfully",
        )


## ------------------------------------------------  Include Routers ------------------------------------------------ ##
router.include_router(protected_router)
