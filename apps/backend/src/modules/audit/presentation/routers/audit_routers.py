from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.audit.audit_container import get_audit_container
from src.modules.audit.presentation.schemas.audit_schemas import (
    AuditEventListResponseSchema,
    AuditEventResponseSchema,
)
from src.shared.dependencies.access_guard import AccessContext, require_access
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.db import get_async_session

audit_access_dep = require_access(
    authenticated=True,
    email_verified=True,
    onboarded=True,
    organization_member=True,
)
router = APIRouter(dependencies=[Depends(audit_access_dep)])
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    "/events",
    response_model=CustomSuccessResponseSchema[AuditEventListResponseSchema],
)
async def list_audit_events(
    session: AsyncSessionDep,
    access_context: Annotated[AccessContext, Depends(audit_access_dep)],
    action: str | None = Query(default=None),
    entity_table: str | None = Query(default=None),
    actor_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Centralized audit stream endpoint. Scoped by organization.
    """
    if access_context.organization is None or access_context.organization.id is None:
        raise ServerError(
            error="Organization context is missing for audit endpoint",
            errors={"code": "ORGANIZATION_CONTEXT_MISSING"},
        )

    audit_container = get_audit_container(session)
    audit_log_domain_service = audit_container.audit_log_domain_service()
    events, total = await audit_log_domain_service.list_events(
        organization_id=access_context.organization.id,
        action=action,
        entity_table=entity_table,
        actor_id=actor_id,
        limit=limit,
        offset=offset,
    )

    items = []
    for event in events:
        # A persisted audit row always has an id; surface any inconsistency
        # instead of silently masking a missing id as 0.
        if event.id is None:
            raise ServerError(
                error="Audit event is missing its identifier",
                internal_details=f"audit event uuid={event.uuid} has no id",
            )
        items.append(
            AuditEventResponseSchema(
                id=event.id,
                uuid=event.uuid,
                action=event.action,
                entity_table=event.entity_table,
                entity_id=event.entity_id,
                organization_id=event.organization_id,
                before_data=event.before_data,
                after_data=event.after_data,
                actor_id=event.actor_id,
                request_id=event.request_id,
                client_ip=event.client_ip,
                client_country=event.client_country,
                client_city=event.client_city,
                user_agent=event.user_agent,
                created_at=event.created_at,
            )
        )

    return cr.success(
        data=AuditEventListResponseSchema(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        ).model_dump(),
        message="Audit events retrieved successfully",
    )
