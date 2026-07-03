from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED

from src.core.utils.response import CustomResponse as cr
from src.core.utils.response import CustomSuccessResponseSchema
from src.modules.motivation.application.usecases.add_motivation_color_usecase import (
    AddMotivationColorUseCase,
)
from src.modules.motivation.application.usecases.create_motivation_quote_usecase import (
    CreateMotivationQuoteUseCase,
)
from src.modules.motivation.application.usecases.delete_motivation_quote_usecase import (
    DeleteMotivationQuoteUseCase,
)
from src.modules.motivation.application.usecases.get_daily_motivation_config_usecase import (
    GetDailyMotivationConfigUseCase,
)
from src.modules.motivation.application.usecases.get_daily_motivation_quote_usecase import (
    GetDailyMotivationQuoteUseCase,
)
from src.modules.motivation.application.usecases.get_motivation_quote_detail_usecase import (
    GetMotivationQuoteDetailUseCase,
)
from src.modules.motivation.application.usecases.get_motivation_quote_preview_slider_usecase import (
    GetMotivationQuotePreviewSliderUseCase,
)
from src.modules.motivation.application.usecases.list_motivation_colors_usecase import (
    ListMotivationColorsUseCase,
)
from src.modules.motivation.application.usecases.list_motivation_quotes_usecase import (
    ListMotivationQuotesUseCase,
)
from src.modules.motivation.application.usecases.list_system_motivation_quotes_usecase import (
    ListSystemMotivationQuotesUseCase,
)
from src.modules.motivation.application.usecases.react_to_motivation_quote_usecase import (
    ReactToMotivationQuoteUseCase,
)
from src.modules.motivation.application.usecases.update_daily_motivation_config_usecase import (
    UpdateDailyMotivationConfigUseCase,
)
from src.modules.motivation.application.usecases.update_motivation_quote_usecase import (
    UpdateMotivationQuoteUseCase,
)
from src.modules.motivation.infrastructure.uow.motivation_uow import MotivationUOW
from src.modules.motivation.motivation_container import get_motivation_container
from src.modules.motivation.presentation.schemas.motivation_schemas import (
    AddMotivationColorRequestSchema,
    CreateMotivationQuoteRequestSchema,
    DailyMotivationConfigResponseSchema,
    MotivationColorListResponseSchema,
    MotivationColorResponseSchema,
    MotivationQuoteListResponseSchema,
    MotivationQuoteReactionResponseSchema,
    MotivationQuoteResponseSchema,
    ReactToMotivationQuoteRequestSchema,
    UpdateDailyMotivationConfigRequestSchema,
    UpdateMotivationQuoteRequestSchema,
)
from src.modules.organization.domain.services.organization_member_domain_service import (
    OrganizationMemberDomainService,
)
from src.modules.organization.infrastructure.repositories.organization_member_repository_impl import (
    OrganizationMemberRepositoryImpl,
)
from src.shared.dependencies.access_guard import require_access
from src.shared.exceptions.base_exceptions import InvalidError
from src.shared.infrastructure.db import get_async_session

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

system_quote_router = APIRouter(
    dependencies=[
        Depends(
            require_access(
                authenticated=True,
                email_verified=True,
                onboarded=True,
                organization_member=False,
            )
        )
    ]
)

router = APIRouter()

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@private_router.get("/config", response_model=CustomSuccessResponseSchema)
async def get_daily_motivation_config(
    request: Request,
    session: AsyncSessionDep,
):
    """
    Get daily motivation config of current organization.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: GetDailyMotivationConfigUseCase = (
            container.get_daily_motivation_config_usecase()
        )

        config = await usecase.execute(
            organization_id=request.state.organization_id,
            actor_id=request.state.user_id,
        )

        payload = {
            "config": DailyMotivationConfigResponseSchema.model_validate(
                config
            ).model_dump()
        }

    return cr.success(
        data=payload,
        message="Daily motivation config retrieved successfully",
    )


@private_router.patch("/config", response_model=CustomSuccessResponseSchema)
async def update_daily_motivation_config(
    request: Request,
    body: UpdateDailyMotivationConfigRequestSchema,
    session: AsyncSessionDep,
):
    """
    Update daily motivation config of current organization.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: UpdateDailyMotivationConfigUseCase = (
            container.update_daily_motivation_config_usecase()
        )

        config = await usecase.execute(
            payload=body,
            organization_id=request.state.organization_id,
            actor_id=request.state.user_id,
        )

        payload = {
            "config": DailyMotivationConfigResponseSchema.model_validate(
                config
            ).model_dump()
        }

    return cr.success(
        data=payload,
        message="Daily motivation config updated successfully",
    )


@private_router.get(
    "/colors",
    response_model=CustomSuccessResponseSchema[MotivationColorListResponseSchema],
)
async def list_motivation_colors(
    request: Request,
    session: AsyncSessionDep,
):
    """
    List motivation colors of current organization.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: ListMotivationColorsUseCase = (
            container.list_motivation_colors_usecase()
        )

        colors = await usecase.execute(
            organization_id=request.state.organization_id,
            actor_id=request.state.user_id,
        )

        items = [
            MotivationColorResponseSchema.model_validate(color) for color in colors
        ]

        payload = MotivationColorListResponseSchema(
            items=items,
        )

    return cr.success(
        data=payload.model_dump(),
        message="Motivation colors listed successfully",
    )


@private_router.post(
    "/colors",
    response_model=CustomSuccessResponseSchema,
)
async def add_motivation_color(
    request: Request,
    body: AddMotivationColorRequestSchema,
    session: AsyncSessionDep,
):
    """
    Add motivation color for current organization.

    Queue behavior:
    A B C D E + G = B C D E G
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: AddMotivationColorUseCase = container.add_motivation_color_usecase()

        color = await usecase.execute(
            payload=body,
            organization_id=request.state.organization_id,
            actor_id=request.state.user_id,
        )

        payload = {
            "color": MotivationColorResponseSchema.model_validate(color).model_dump()
        }

    return cr.success(
        data=payload,
        message="Motivation color added successfully",
        status_code=HTTP_201_CREATED,
    )


@private_router.post("/quotes", response_model=CustomSuccessResponseSchema)
async def create_motivation_quote(
    request: Request,
    body: CreateMotivationQuoteRequestSchema,
    session: AsyncSessionDep,
):
    """
    Create custom motivation quote for current organization.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: CreateMotivationQuoteUseCase = (
            container.create_motivation_quote_usecase()
        )

        quote = await usecase.execute(
            payload=body,
            organization_id=request.state.organization_id,
            actor_id=request.state.user_id,
        )

        payload = {
            "quote": MotivationQuoteResponseSchema.model_validate(quote).model_dump()
        }

    return cr.success(
        data=payload,
        message="Motivation quote created successfully",
        status_code=HTTP_201_CREATED,
    )


@private_router.get(
    "/quotes",
    response_model=CustomSuccessResponseSchema[MotivationQuoteListResponseSchema],
)
async def list_motivation_quotes(
    request: Request,
    session: AsyncSessionDep,
    status: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
):
    """
    List custom motivation quotes of current organization.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: ListMotivationQuotesUseCase = (
            container.list_motivation_quotes_usecase()
        )

        quotes = await usecase.execute(
            organization_id=request.state.organization_id,
            status=status,
            search=search,
        )

        items = [
            MotivationQuoteResponseSchema.model_validate(quote) for quote in quotes
        ]

        payload = MotivationQuoteListResponseSchema(
            items=items,
            total=len(items),
        )

    return cr.success(
        data=payload.model_dump(),
        message="Motivation quotes listed successfully",
    )


@private_router.get(
    "/quotes/previews",
    response_model=CustomSuccessResponseSchema[MotivationQuoteListResponseSchema],
)
async def get_motivation_quote_preview_slider(
    request: Request,
    session: AsyncSessionDep,
):
    """
    Get motivation quotes for preview/slider.

    Logic:
    1. If active custom quotes exist, return up to 3 custom quotes.
    2. If no active custom quotes exist, return up to 3 system quotes.
    3. If both exist, custom quotes are prioritized.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: GetMotivationQuotePreviewSliderUseCase = (
            container.get_motivation_quote_preview_slider_usecase()
        )

        quotes = await usecase.execute(
            organization_id=request.state.organization_id,
        )

        items = [
            MotivationQuoteResponseSchema.model_validate(quote) for quote in quotes
        ]

        payload = MotivationQuoteListResponseSchema(
            items=items,
            total=len(items),
        )

    return cr.success(
        data=payload.model_dump(),
        message="Motivation quote preview slider retrieved successfully",
    )


@private_router.get(
    "/quotes/{quote_uuid}",
    response_model=CustomSuccessResponseSchema,
)
async def get_motivation_quote_detail(
    request: Request,
    quote_uuid: str,
    session: AsyncSessionDep,
):
    """
    Get one custom motivation quote detail.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: GetMotivationQuoteDetailUseCase = (
            container.get_motivation_quote_detail_usecase()
        )

        quote = await usecase.execute(
            quote_uuid=quote_uuid,
            organization_id=request.state.organization_id,
        )

        payload = {
            "quote": MotivationQuoteResponseSchema.model_validate(quote).model_dump()
        }

    return cr.success(
        data=payload,
        message="Motivation quote detail retrieved successfully",
    )


@private_router.patch(
    "/quotes/{quote_uuid}",
    response_model=CustomSuccessResponseSchema,
)
async def update_motivation_quote(
    request: Request,
    quote_uuid: str,
    body: UpdateMotivationQuoteRequestSchema,
    session: AsyncSessionDep,
):
    """
    Update custom motivation quote.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: UpdateMotivationQuoteUseCase = (
            container.update_motivation_quote_usecase()
        )

        quote = await usecase.execute(
            quote_uuid=quote_uuid,
            payload=body,
            organization_id=request.state.organization_id,
            actor_id=request.state.user_id,
        )

        payload = {
            "quote": MotivationQuoteResponseSchema.model_validate(quote).model_dump()
        }

    return cr.success(
        data=payload,
        message="Motivation quote updated successfully",
    )


@private_router.delete(
    "/quotes/{quote_uuid}",
    response_model=CustomSuccessResponseSchema,
)
async def delete_motivation_quote(
    request: Request,
    quote_uuid: str,
    session: AsyncSessionDep,
):
    """
    Delete custom motivation quote.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: DeleteMotivationQuoteUseCase = (
            container.delete_motivation_quote_usecase()
        )

        quote = await usecase.execute(
            quote_uuid=quote_uuid,
            organization_id=request.state.organization_id,
            actor_id=request.state.user_id,
        )

        payload = {
            "quote_uuid": quote.uuid,
        }

    return cr.success(
        data=payload,
        message="Motivation quote deleted successfully",
    )


@private_router.get(
    "/system-quotes",
    response_model=CustomSuccessResponseSchema[MotivationQuoteListResponseSchema],
)
async def list_system_motivation_quotes(
    request: Request,
    session: AsyncSessionDep,
    status: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
):
    """
    List system default motivation quotes for the active organization.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: ListSystemMotivationQuotesUseCase = (
            container.list_system_motivation_quotes_usecase()
        )

        quotes = await usecase.execute(
            organization_id=request.state.organization_id,
            status=status,
            search=search,
        )

        items = [
            MotivationQuoteResponseSchema.model_validate(quote) for quote in quotes
        ]

        payload = MotivationQuoteListResponseSchema(
            items=items,
            total=len(items),
        )

    return cr.success(
        data=payload.model_dump(),
        message="System motivation quotes listed successfully",
    )


@private_router.get("/daily-quote", response_model=CustomSuccessResponseSchema)
async def get_daily_motivation_quote(
    request: Request,
    session: AsyncSessionDep,
):
    """
    Get quote that should be displayed today.
    """

    async with MotivationUOW(session):
        container = get_motivation_container(session)
        usecase: GetDailyMotivationQuoteUseCase = (
            container.get_daily_motivation_quote_usecase()
        )

        quote = await usecase.execute(
            organization_id=request.state.organization_id,
        )

        payload = {
            "quote": (
                MotivationQuoteResponseSchema.model_validate(quote).model_dump()
                if quote
                else None
            )
        }

    return cr.success(
        data=payload,
        message="Daily motivation quote retrieved successfully",
    )


@private_router.post("/reactions", response_model=CustomSuccessResponseSchema)
async def react_to_motivation_quote(
    request: Request,
    body: ReactToMotivationQuoteRequestSchema,
    session: AsyncSessionDep,
):
    """
    React to a motivation quote.
    """

    async with MotivationUOW(session):
        organization_member_domain_service = OrganizationMemberDomainService(
            repository=OrganizationMemberRepositoryImpl(session=session)
        )

        organization_member = (
            await organization_member_domain_service.get_member_by_user_id(
                organization_id=request.state.organization_id,
                user_id=request.state.user_id,
            )
        )

        if not organization_member or not organization_member.id:
            raise InvalidError("Organization member id not found")

        container = get_motivation_container(session)
        usecase: ReactToMotivationQuoteUseCase = (
            container.react_to_motivation_quote_usecase()
        )

        reaction = await usecase.execute(
            payload=body,
            organization_id=request.state.organization_id,
            member_id=organization_member.id,
            actor_id=request.state.user_id,
        )

        payload = {
            "reaction": MotivationQuoteReactionResponseSchema.model_validate(
                reaction
            ).model_dump()
        }

    return cr.success(
        data=payload,
        message="Motivation quote reaction saved successfully",
    )


router.include_router(private_router)
router.include_router(system_quote_router)
