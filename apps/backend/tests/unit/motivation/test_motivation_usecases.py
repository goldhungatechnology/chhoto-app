from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


ORG_ID = 1
ACTOR_ID = 1
MEMBER_ID = 1
CONFIG_ID = 1
QUOTE_ID = 1
QUOTE_UUID = "10d7e708-7bdd-4184-980a-cf05c815f8cf"
COLOR_ID = 1
HEX_COLOR = "#7C3AED"


def _make_config(**overrides):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    data = {
        "id": CONFIG_ID,
        "uuid": "config-uuid",
        "organization_id": ORG_ID,
        "sys_quote_source": True,
        "is_enabled": True,
        "allow_reactions": True,
        "display_time": "09:00 AM",
        "font_style": "arial",
    }
    data.update(overrides)
    return DailyMotivationConfigEntity(**data)


def _make_quote(**overrides):
    from src.modules.motivation.domain.entities.motivation_quote_entity import (
        MotivationQuoteEntity,
    )

    data = {
        "id": QUOTE_ID,
        "uuid": QUOTE_UUID,
        "organization_id": ORG_ID,
        "context": "Stay focused and keep growing.",
        "author_name": "System",
        "is_sys_default": False,
        "status": "active",
        "font_style": "arial",
        "theme_color": HEX_COLOR,
        "bg_image": None,
    }
    data.update(overrides)
    return MotivationQuoteEntity(**data)


def _make_color(**overrides):
    from src.modules.motivation.domain.entities.motivation_color_entity import (
        MotivationColorEntity,
    )

    data = {
        "id": COLOR_ID,
        "uuid": "color-uuid",
        "config_id": CONFIG_ID,
        "color_code": HEX_COLOR,
    }
    data.update(overrides)
    return MotivationColorEntity(**data)


def _make_reaction(**overrides):
    from src.modules.motivation.domain.entities.motivation_quote_reaction_entity import (
        MotivationQuoteReactionEntity,
    )

    data = {
        "id": 1,
        "uuid": "reaction-uuid",
        "organization_id": ORG_ID,
        "member_id": MEMBER_ID,
        "quote_id": QUOTE_ID,
        "reaction_type": "like",
    }
    data.update(overrides)
    return MotivationQuoteReactionEntity(**data)


def _make_update_config_payload(**overrides):
    from src.modules.motivation.domain.enums.motivation_enums import (
        QuotesTextStyleEnum,
    )
    from src.modules.motivation.presentation.schemas.motivation_schemas import (
        UpdateDailyMotivationConfigRequestSchema,
    )

    data = {
        "sys_quote_source": True,
        "is_enabled": True,
        "allow_reactions": True,
        "display_time": "09:00 AM",
        "font_style": QuotesTextStyleEnum.ARIAL,
    }
    data.update(overrides)
    return UpdateDailyMotivationConfigRequestSchema(**data)


def _make_create_quote_payload(**overrides):
    from src.modules.motivation.domain.enums.motivation_enums import (
        QuotesTextStyleEnum,
    )
    from src.modules.motivation.presentation.schemas.motivation_schemas import (
        CreateMotivationQuoteRequestSchema,
    )

    data = {
        "context": "Stay focused and keep growing.",
        "author_name": "System",
        "font_style": QuotesTextStyleEnum.ARIAL,
        "theme_color": HEX_COLOR,
        "bg_image": None,
        "status": None,
    }
    data.update(overrides)
    return CreateMotivationQuoteRequestSchema(**data)


def _make_update_quote_payload(**overrides):
    from src.modules.motivation.domain.enums.motivation_enums import (
        QuotesStatusEnum,
        QuotesTextStyleEnum,
    )
    from src.modules.motivation.presentation.schemas.motivation_schemas import (
        UpdateMotivationQuoteRequestSchema,
    )

    data = {
        "context": "Updated quote",
        "author_name": "Admin",
        "status": QuotesStatusEnum.INACTIVE,
        "font_style": QuotesTextStyleEnum.ARIAL,
        "theme_color": "#F59E0B",
        "bg_image": None,
    }
    data.update(overrides)
    return UpdateMotivationQuoteRequestSchema(**data)


def _make_color_payload(**overrides):
    from src.modules.motivation.presentation.schemas.motivation_schemas import (
        AddMotivationColorRequestSchema,
    )

    data = {
        "color_code": HEX_COLOR,
    }
    data.update(overrides)
    return AddMotivationColorRequestSchema(**data)


def _make_reaction_payload(**overrides):
    from src.modules.motivation.presentation.schemas.motivation_schemas import (
        ReactToMotivationQuoteRequestSchema,
    )

    data = {
        "quote_uuid": QUOTE_UUID,
        "reaction_type": "like",
    }
    data.update(overrides)
    return ReactToMotivationQuoteRequestSchema(**data)


@pytest_asyncio.fixture
async def get_daily_motivation_config_usecase():
    from src.modules.motivation.application.usecases.get_daily_motivation_config_usecase import (
        GetDailyMotivationConfigUseCase,
    )

    service = AsyncMock()
    return GetDailyMotivationConfigUseCase(
        daily_motivation_config_domain_service=service,
    )


@pytest_asyncio.fixture
async def update_daily_motivation_config_usecase():
    from src.modules.motivation.application.usecases.update_daily_motivation_config_usecase import (
        UpdateDailyMotivationConfigUseCase,
    )

    service = AsyncMock()
    return UpdateDailyMotivationConfigUseCase(
        daily_motivation_config_domain_service=service,
    )


@pytest_asyncio.fixture
async def create_motivation_quote_usecase():
    from src.modules.motivation.application.usecases.create_motivation_quote_usecase import (
        CreateMotivationQuoteUseCase,
    )

    service = AsyncMock()
    return CreateMotivationQuoteUseCase(
        motivation_quote_domain_service=service,
    )


@pytest_asyncio.fixture
async def list_motivation_quotes_usecase():
    from src.modules.motivation.application.usecases.list_motivation_quotes_usecase import (
        ListMotivationQuotesUseCase,
    )

    service = AsyncMock()
    return ListMotivationQuotesUseCase(
        motivation_quote_domain_service=service,
    )


@pytest_asyncio.fixture
async def get_motivation_quote_detail_usecase():
    from src.modules.motivation.application.usecases.get_motivation_quote_detail_usecase import (
        GetMotivationQuoteDetailUseCase,
    )

    service = AsyncMock()
    return GetMotivationQuoteDetailUseCase(
        motivation_quote_domain_service=service,
    )


@pytest_asyncio.fixture
async def update_motivation_quote_usecase():
    from src.modules.motivation.application.usecases.update_motivation_quote_usecase import (
        UpdateMotivationQuoteUseCase,
    )

    service = AsyncMock()
    return UpdateMotivationQuoteUseCase(
        motivation_quote_domain_service=service,
    )


@pytest_asyncio.fixture
async def delete_motivation_quote_usecase():
    from src.modules.motivation.application.usecases.delete_motivation_quote_usecase import (
        DeleteMotivationQuoteUseCase,
    )

    service = AsyncMock()
    return DeleteMotivationQuoteUseCase(
        motivation_quote_domain_service=service,
    )


@pytest_asyncio.fixture
async def get_daily_motivation_quote_usecase():
    from src.modules.motivation.application.usecases.get_daily_motivation_quote_usecase import (
        GetDailyMotivationQuoteUseCase,
    )

    service = AsyncMock()
    return GetDailyMotivationQuoteUseCase(
        motivation_quote_domain_service=service,
    )


@pytest_asyncio.fixture
async def list_motivation_colors_usecase():
    from src.modules.motivation.application.usecases.list_motivation_colors_usecase import (
        ListMotivationColorsUseCase,
    )

    config_service = AsyncMock()
    color_service = AsyncMock()
    return ListMotivationColorsUseCase(
        config_domain_service=config_service,
        color_domain_service=color_service,
    )


@pytest_asyncio.fixture
async def add_motivation_color_usecase():
    from src.modules.motivation.application.usecases.add_motivation_color_usecase import (
        AddMotivationColorUseCase,
    )

    config_service = AsyncMock()
    color_service = AsyncMock()
    return AddMotivationColorUseCase(
        config_domain_service=config_service,
        color_domain_service=color_service,
    )


@pytest_asyncio.fixture
async def react_to_motivation_quote_usecase():
    from src.modules.motivation.application.usecases.react_to_motivation_quote_usecase import (
        ReactToMotivationQuoteUseCase,
    )

    service = AsyncMock()
    return ReactToMotivationQuoteUseCase(
        motivation_quote_reaction_domain_service=service,
    )


@pytest.mark.asyncio
async def test_get_daily_motivation_config_success(
    get_daily_motivation_config_usecase,
):
    config = _make_config()

    service = get_daily_motivation_config_usecase.daily_motivation_config_domain_service
    service.get_or_create_default_config = AsyncMock(return_value=config)

    result = await get_daily_motivation_config_usecase.execute(
        organization_id=ORG_ID,
        actor_id=ACTOR_ID,
    )

    assert result == config
    service.get_or_create_default_config.assert_awaited_once_with(
        organization_id=ORG_ID,
        actor_id=ACTOR_ID,
    )


@pytest.mark.asyncio
async def test_update_daily_motivation_config_success(
    update_daily_motivation_config_usecase,
):
    payload = _make_update_config_payload(is_enabled=False)
    config = _make_config(is_enabled=False)

    service = (
        update_daily_motivation_config_usecase.daily_motivation_config_domain_service
    )
    service.update_config = AsyncMock(return_value=config)

    result = await update_daily_motivation_config_usecase.execute(
        payload=payload,
        organization_id=ORG_ID,
        actor_id=ACTOR_ID,
    )

    assert result == config
    service.update_config.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_motivation_quote_success(
    create_motivation_quote_usecase,
):
    payload = _make_create_quote_payload()
    quote = _make_quote()

    service = create_motivation_quote_usecase.motivation_quote_domain_service
    service.create_custom_quote = AsyncMock(return_value=quote)

    result = await create_motivation_quote_usecase.execute(
        payload=payload,
        organization_id=ORG_ID,
        actor_id=ACTOR_ID,
    )

    assert result == quote
    service.create_custom_quote.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_motivation_quotes_success(
    list_motivation_quotes_usecase,
):
    quotes = [
        _make_quote(id=1),
        _make_quote(id=2, uuid="second-uuid", context="Second quote"),
    ]

    service = list_motivation_quotes_usecase.motivation_quote_domain_service
    service.list_custom_quotes = AsyncMock(return_value=quotes)

    result = await list_motivation_quotes_usecase.execute(
        organization_id=ORG_ID,
        status="active",
        search="focused",
    )

    assert result == quotes
    service.list_custom_quotes.assert_awaited_once_with(
        organization_id=ORG_ID,
        status="active",
        search="focused",
    )


@pytest.mark.asyncio
async def test_get_motivation_quote_detail_success(
    get_motivation_quote_detail_usecase,
):
    quote = _make_quote()

    service = get_motivation_quote_detail_usecase.motivation_quote_domain_service
    service.get_quote_by_uuid = AsyncMock(return_value=quote)

    result = await get_motivation_quote_detail_usecase.execute(
        quote_uuid=QUOTE_UUID,
        organization_id=ORG_ID,
    )

    assert result == quote
    service.get_quote_by_uuid.assert_awaited_once_with(
        quote_uuid=QUOTE_UUID,
        organization_id=ORG_ID,
    )


@pytest.mark.asyncio
async def test_update_motivation_quote_success(
    update_motivation_quote_usecase,
):
    payload = _make_update_quote_payload()
    quote = _make_quote(context="Updated quote", status="inactive")

    service = update_motivation_quote_usecase.motivation_quote_domain_service
    service.update_custom_quote = AsyncMock(return_value=quote)

    result = await update_motivation_quote_usecase.execute(
        quote_uuid=QUOTE_UUID,
        payload=payload,
        organization_id=ORG_ID,
        actor_id=ACTOR_ID,
    )

    assert result == quote
    service.update_custom_quote.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_motivation_quote_success(
    delete_motivation_quote_usecase,
):
    quote = _make_quote()

    service = delete_motivation_quote_usecase.motivation_quote_domain_service
    service.delete_custom_quote = AsyncMock(return_value=quote)

    result = await delete_motivation_quote_usecase.execute(
        quote_uuid=QUOTE_UUID,
        organization_id=ORG_ID,
        actor_id=ACTOR_ID,
    )

    assert result == quote
    service.delete_custom_quote.assert_awaited_once_with(
        organization_id=ORG_ID,
        quote_uuid=QUOTE_UUID,
        actor_id=ACTOR_ID,
    )


@pytest.mark.asyncio
async def test_get_daily_motivation_quote_success(
    get_daily_motivation_quote_usecase,
):
    quote = _make_quote()

    service = get_daily_motivation_quote_usecase.motivation_quote_domain_service
    service.get_daily_quote = AsyncMock(return_value=quote)

    result = await get_daily_motivation_quote_usecase.execute(
        organization_id=ORG_ID,
    )

    assert result == quote
    service.get_daily_quote.assert_awaited_once_with(
        organization_id=ORG_ID,
    )


@pytest.mark.asyncio
async def test_get_daily_motivation_quote_returns_none(
    get_daily_motivation_quote_usecase,
):
    service = get_daily_motivation_quote_usecase.motivation_quote_domain_service
    service.get_daily_quote = AsyncMock(return_value=None)

    result = await get_daily_motivation_quote_usecase.execute(
        organization_id=ORG_ID,
    )

    assert result is None


@pytest.mark.asyncio
async def test_list_motivation_colors_success(
    list_motivation_colors_usecase,
):
    config = _make_config(id=CONFIG_ID)
    colors = [
        _make_color(id=1, color_code="#7C3AED"),
        _make_color(id=2, uuid="color-uuid-2", color_code="#F59E0B"),
    ]

    list_motivation_colors_usecase.config_domain_service.get_or_create_default_config = AsyncMock(
        return_value=config
    )
    list_motivation_colors_usecase.color_domain_service.list_colors = AsyncMock(
        return_value=colors
    )

    result = await list_motivation_colors_usecase.execute(
        organization_id=ORG_ID,
        actor_id=ACTOR_ID,
    )

    assert result == colors
    list_motivation_colors_usecase.color_domain_service.list_colors.assert_awaited_once_with(
        config_id=CONFIG_ID,
        actor_id=ACTOR_ID,
    )


@pytest.mark.asyncio
async def test_add_motivation_color_success(
    add_motivation_color_usecase,
):
    payload = _make_color_payload(color_code="#F59E0B")
    config = _make_config(id=CONFIG_ID)
    color = _make_color(color_code="#F59E0B")

    add_motivation_color_usecase.config_domain_service.get_or_create_default_config = (
        AsyncMock(return_value=config)
    )
    add_motivation_color_usecase.color_domain_service.add_color = AsyncMock(
        return_value=color
    )

    result = await add_motivation_color_usecase.execute(
        organization_id=ORG_ID,
        actor_id=ACTOR_ID,
        payload=payload,
    )

    assert result == color
    add_motivation_color_usecase.color_domain_service.add_color.assert_awaited_once_with(
        config_id=CONFIG_ID,
        color_code="#F59E0B",
        actor_id=ACTOR_ID,
    )


@pytest.mark.asyncio
async def test_react_to_motivation_quote_success(
    react_to_motivation_quote_usecase,
):
    payload = _make_reaction_payload()
    reaction = _make_reaction()

    service = react_to_motivation_quote_usecase.motivation_quote_reaction_domain_service
    service.add_or_update_reaction = AsyncMock(return_value=reaction)

    result = await react_to_motivation_quote_usecase.execute(
        payload=payload,
        organization_id=ORG_ID,
        member_id=MEMBER_ID,
        actor_id=ACTOR_ID,
    )

    assert result == reaction
    service.add_or_update_reaction.assert_awaited_once_with(
        organization_id=ORG_ID,
        member_id=MEMBER_ID,
        quote_uuid=QUOTE_UUID,
        reaction_type="like",
        actor_id=ACTOR_ID,
    )


@pytest.mark.asyncio
async def test_get_daily_motivation_config_usecase_re_raises_domain_error(
    get_daily_motivation_config_usecase,
):
    from src.shared.exceptions.base_exceptions import DomainError

    usecase = get_daily_motivation_config_usecase
    service = usecase.daily_motivation_config_domain_service
    service.get_or_create_default_config = AsyncMock(
        side_effect=DomainError(error="domain error"),
    )

    with pytest.raises(DomainError):
        await usecase.execute(
            organization_id=ORG_ID,
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_get_daily_motivation_quote_usecase_re_raises_domain_error(
    get_daily_motivation_quote_usecase,
):
    from src.shared.exceptions.base_exceptions import DomainError

    usecase = get_daily_motivation_quote_usecase
    service = usecase.motivation_quote_domain_service
    service.get_daily_quote = AsyncMock(
        side_effect=DomainError(error="domain error"),
    )

    with pytest.raises(DomainError):
        await usecase.execute(
            organization_id=ORG_ID,
        )


@pytest.mark.asyncio
async def test_get_daily_motivation_config_usecase_wraps_unexpected_error_in_server_error(
    get_daily_motivation_config_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    usecase = get_daily_motivation_config_usecase
    service = usecase.daily_motivation_config_domain_service
    service.get_or_create_default_config = AsyncMock(
        side_effect=ValueError("unexpected"),
    )

    with pytest.raises(ServerError):
        await usecase.execute(
            organization_id=ORG_ID,
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_get_daily_motivation_quote_usecase_wraps_unexpected_error_in_server_error(
    get_daily_motivation_quote_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    usecase = get_daily_motivation_quote_usecase
    service = usecase.motivation_quote_domain_service
    service.get_daily_quote = AsyncMock(
        side_effect=ValueError("unexpected"),
    )

    with pytest.raises(ServerError):
        await usecase.execute(
            organization_id=ORG_ID,
        )
