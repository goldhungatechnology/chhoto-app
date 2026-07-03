from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.visitor.presentation.schemas.visitor_schemas import (
    ActiveVisitorsCountResponseSchema,
    TopPagesResponseSchema,
    VisitorsByCountryResponseSchema,
    VisitorSchema,
    VisitorsResponseSchema,
)
from src.modules.visitor.visitor_container import get_visitor_container
from src.shared.dependencies.access_guard import require_access
from src.shared.infrastructure.db import get_async_session

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]

private_router = APIRouter(
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


@private_router.get(
    "/analytics/",
    response_model=CustomSuccessResponseSchema[VisitorsResponseSchema],
)
async def list_visitors(request: Request, session: AsyncSessionDep):
    """List all database visitors for the agent's current organization."""
    usecase = get_visitor_container(session).list_visitors_usecase()
    visitors = await usecase.execute(organization_id=request.state.organization_id)

    items = [
        VisitorSchema(
            uuid=item["visitor"].uuid,
            external_id=item["visitor"].external_id,
            visit_count=item["visitor"].visit_count,
            is_identified=item["visitor"].is_identified,
            last_seen_at=item["visitor"].last_seen_at.isoformat(),
            name=item["visitor"].name,
            email=item["visitor"].email,
            phone=item["visitor"].phone,
            current_page=item["current_page"],
            device=item["device"],
            browser=item["browser"],
            ip_address=item["ip_address"],
            active_duration=item["active_duration"],
        )
        for item in visitors
    ]

    return cr.success(
        data=VisitorsResponseSchema(items=items, total=len(items)).model_dump(),
        message="Visitors retrieved successfully",
    )


@private_router.get(
    "/analytics/by-country",
    response_model=CustomSuccessResponseSchema[VisitorsByCountryResponseSchema],
)
async def get_visitors_by_country(request: Request, session: AsyncSessionDep):
    """Retrieve visitors grouped and aggregated by country."""
    usecase = get_visitor_container(session).get_visitors_by_country_usecase()
    result = await usecase.execute(organization_id=request.state.organization_id)
    return cr.success(
        data=VisitorsByCountryResponseSchema(**result).model_dump(),
        message="Visitors by country retrieved successfully",
    )


@private_router.get(
    "/analytics/top-pages",
    response_model=CustomSuccessResponseSchema[TopPagesResponseSchema],
)
async def get_top_pages(request: Request, session: AsyncSessionDep):
    """Retrieve top 5 visited pages grouped and aggregated."""
    usecase = get_visitor_container(session).get_top_pages_usecase()
    result = await usecase.execute(organization_id=request.state.organization_id)
    return cr.success(
        data=TopPagesResponseSchema(**result).model_dump(),
        message="Top pages retrieved successfully",
    )


@private_router.get(
    "/analytics/stat-cards",
    response_model=CustomSuccessResponseSchema[ActiveVisitorsCountResponseSchema],
)
async def get_active_count(request: Request, session: AsyncSessionDep):
    """Retrieve the total stats cards info of active visitors."""
    usecase = get_visitor_container(session).get_active_visitors_usecase()
    active_visitors = await usecase.execute(
        organization_id=request.state.organization_id
    )
    return cr.success(
        data=ActiveVisitorsCountResponseSchema(count=len(active_visitors)).model_dump(),
        message="Active visitor count retrieved successfully",
    )


router.include_router(private_router)
