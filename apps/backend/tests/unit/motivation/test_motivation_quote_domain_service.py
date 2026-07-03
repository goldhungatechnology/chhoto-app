from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


QUOTE_UUID = "10d7e708-7bdd-4184-980a-cf05c815f8cf"
ORG_ID = 1
ACTOR_ID = 1
HEX_COLOR = "#7C3AED"
FONT_STYLE = "arial"


@pytest_asyncio.fixture
async def motivation_quote_domain_service():
    from src.modules.motivation.domain.services.motivation_quote_domain_service import (
        MotivationQuoteDomainService,
    )

    mock_quote_repo = AsyncMock()
    mock_quote_repo.session = None
    mock_quote_repo.add = AsyncMock()
    mock_quote_repo.update = AsyncMock()
    mock_quote_repo.get_by = AsyncMock()
    mock_quote_repo.list_by_organization_id = AsyncMock()
    mock_quote_repo.get_active_custom_quote = AsyncMock()
    mock_quote_repo.get_active_system_quote = AsyncMock()

    mock_config_repo = AsyncMock()
    mock_config_repo.get_by_organization_id = AsyncMock()

    return MotivationQuoteDomainService(
        quote_repository=mock_quote_repo,
        config_repository=mock_config_repo,
    )


def make_quote(**kwargs):
    from src.modules.motivation.domain.entities.motivation_quote_entity import (
        MotivationQuoteEntity,
    )

    data = {
        "id": 1,
        "uuid": QUOTE_UUID,
        "organization_id": ORG_ID,
        "context": "Stay focused and keep growing.",
        "author_name": "System",
        "is_sys_default": False,
        "status": "active",
        "font_style": FONT_STYLE,
        "theme_color": HEX_COLOR,
        "bg_image": None,
    }
    data.update(kwargs)

    return MotivationQuoteEntity(**data)


def make_config(**kwargs):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    data = {
        "id": 1,
        "organization_id": ORG_ID,
        "sys_quote_source": True,
        "is_enabled": True,
        "allow_reactions": True,
    }
    data.update(kwargs)

    return DailyMotivationConfigEntity(**data)


@pytest.mark.asyncio
async def test_create_custom_quote_with_empty_context_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    quote = make_quote(context="")

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.create_custom_quote(
            quote_entity=quote,
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_create_custom_quote_with_invalid_status_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    quote = make_quote(status="wrong")

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.create_custom_quote(
            quote_entity=quote,
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_create_custom_quote_without_organization_id_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    quote = make_quote(organization_id=None)

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.create_custom_quote(
            quote_entity=quote,
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_create_custom_quote_success(motivation_quote_domain_service):
    quote = make_quote()

    motivation_quote_domain_service.quote_repository.add = AsyncMock(return_value=quote)

    created = await motivation_quote_domain_service.create_custom_quote(
        quote_entity=quote,
        actor_id=ACTOR_ID,
    )

    assert created == quote
    assert created.is_sys_default is False
    assert created.created_by_id == ACTOR_ID
    assert created.theme_color == HEX_COLOR


@pytest.mark.asyncio
async def test_list_custom_quotes_success(motivation_quote_domain_service):
    quote = make_quote()

    motivation_quote_domain_service.quote_repository.list_by_organization_id = (
        AsyncMock(return_value=[quote])
    )

    quotes = await motivation_quote_domain_service.list_custom_quotes(
        organization_id=ORG_ID,
        status="active",
        search="focused",
    )

    assert quotes == [quote]


@pytest.mark.asyncio
async def test_list_custom_quotes_with_invalid_status_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.list_custom_quotes(
            organization_id=ORG_ID,
            status="wrong",
        )


@pytest.mark.asyncio
async def test_get_quote_by_uuid_success(motivation_quote_domain_service):
    quote = make_quote()

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=quote
    )

    result = await motivation_quote_domain_service.get_quote_by_uuid(
        quote_uuid=QUOTE_UUID,
        organization_id=ORG_ID,
    )

    assert result == quote


@pytest.mark.asyncio
async def test_get_quote_by_uuid_not_found_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=None
    )

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.get_quote_by_uuid(
            quote_uuid=QUOTE_UUID,
            organization_id=ORG_ID,
        )


@pytest.mark.asyncio
async def test_get_quote_by_uuid_system_quote_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    quote = make_quote(is_sys_default=True)

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=quote
    )

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.get_quote_by_uuid(
            quote_uuid=QUOTE_UUID,
            organization_id=ORG_ID,
        )


@pytest.mark.asyncio
async def test_update_custom_quote_without_uuid_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    quote = make_quote(uuid=None)

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.update_custom_quote(
            quote_entity=quote,
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_update_custom_quote_not_found_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=None
    )

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.update_custom_quote(
            quote_entity=make_quote(context="Updated context"),
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_update_system_quote_from_custom_flow_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    existing_quote = make_quote(is_sys_default=True)

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=existing_quote
    )

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.update_custom_quote(
            quote_entity=make_quote(context="Updated context"),
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_update_custom_quote_success(motivation_quote_domain_service):
    existing_quote = make_quote(
        context="Old context",
        author_name="Old Author",
        status="inactive",
        font_style="georgia",
        theme_color="#000000",
        bg_image=None,
    )

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=existing_quote
    )
    motivation_quote_domain_service.quote_repository.update = AsyncMock(
        return_value=existing_quote
    )

    updated = await motivation_quote_domain_service.update_custom_quote(
        quote_entity=make_quote(
            context="New context",
            author_name="New Author",
            status="active",
            font_style=FONT_STYLE,
            theme_color=HEX_COLOR,
            bg_image="https://cdn.example.com/bg.png",
        ),
        actor_id=ACTOR_ID,
    )

    assert updated.context == "New context"
    assert updated.author_name == "New Author"
    assert updated.status == "active"
    assert updated.font_style == FONT_STYLE
    assert updated.theme_color == HEX_COLOR
    assert updated.bg_image == "https://cdn.example.com/bg.png"
    assert updated.updated_by_id == ACTOR_ID


@pytest.mark.asyncio
async def test_delete_custom_quote_success(motivation_quote_domain_service):
    existing_quote = make_quote()

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=existing_quote
    )
    motivation_quote_domain_service.quote_repository.update = AsyncMock(
        return_value=existing_quote
    )

    deleted = await motivation_quote_domain_service.delete_custom_quote(
        organization_id=ORG_ID,
        quote_uuid=QUOTE_UUID,
        actor_id=ACTOR_ID,
    )

    assert deleted.deleted_at is not None
    assert deleted.updated_by_id == ACTOR_ID


@pytest.mark.asyncio
async def test_delete_custom_quote_not_found_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=None
    )

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.delete_custom_quote(
            organization_id=ORG_ID,
            quote_uuid=QUOTE_UUID,
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_delete_system_quote_from_custom_flow_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    existing_quote = make_quote(is_sys_default=True)

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=existing_quote
    )

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.delete_custom_quote(
            organization_id=ORG_ID,
            quote_uuid=QUOTE_UUID,
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_change_custom_quote_status_success(
    motivation_quote_domain_service,
):
    existing_quote = make_quote(status="inactive")

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=existing_quote
    )
    motivation_quote_domain_service.quote_repository.update = AsyncMock(
        return_value=existing_quote
    )

    updated = await motivation_quote_domain_service.change_custom_quote_status(
        organization_id=ORG_ID,
        quote_uuid=QUOTE_UUID,
        status="active",
        actor_id=ACTOR_ID,
    )

    assert updated.status == "active"
    assert updated.updated_by_id == ACTOR_ID


@pytest.mark.asyncio
async def test_change_custom_quote_status_invalid_status_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.change_custom_quote_status(
            organization_id=ORG_ID,
            quote_uuid=QUOTE_UUID,
            status="wrong",
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_change_custom_quote_status_not_found_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=None
    )

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.change_custom_quote_status(
            organization_id=ORG_ID,
            quote_uuid=QUOTE_UUID,
            status="active",
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_change_system_quote_status_from_custom_flow_raises_invalid_error(
    motivation_quote_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    existing_quote = make_quote(is_sys_default=True)

    motivation_quote_domain_service.quote_repository.get_by = AsyncMock(
        return_value=existing_quote
    )

    with pytest.raises(InvalidError):
        await motivation_quote_domain_service.change_custom_quote_status(
            organization_id=ORG_ID,
            quote_uuid=QUOTE_UUID,
            status="active",
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_get_daily_quote_returns_none_when_config_disabled(
    motivation_quote_domain_service,
):
    config = make_config(is_enabled=False)

    motivation_quote_domain_service.config_repository.get_by_organization_id = (
        AsyncMock(return_value=config)
    )

    quote = await motivation_quote_domain_service.get_daily_quote(
        organization_id=ORG_ID
    )

    assert quote is None
    motivation_quote_domain_service.quote_repository.get_active_custom_quote.assert_not_awaited()
    motivation_quote_domain_service.quote_repository.get_active_system_quote.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_daily_quote_returns_system_when_sys_quote_source_enabled(
    motivation_quote_domain_service,
):
    config = make_config(sys_quote_source=True, is_enabled=True)
    system_quote = make_quote(
        id=2,
        uuid="system-quote-uuid",
        organization_id=None,
        is_sys_default=True,
    )

    motivation_quote_domain_service.config_repository.get_by_organization_id = (
        AsyncMock(return_value=config)
    )
    motivation_quote_domain_service.quote_repository.get_active_system_quote = (
        AsyncMock(return_value=system_quote)
    )

    quote = await motivation_quote_domain_service.get_daily_quote(
        organization_id=ORG_ID
    )

    assert quote == system_quote
    motivation_quote_domain_service.quote_repository.get_active_custom_quote.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_daily_quote_returns_custom_quote_first(
    motivation_quote_domain_service,
):
    custom_quote = make_quote()

    motivation_quote_domain_service.config_repository.get_by_organization_id = (
        AsyncMock(return_value=None)
    )
    motivation_quote_domain_service.quote_repository.get_active_custom_quote = (
        AsyncMock(return_value=custom_quote)
    )

    quote = await motivation_quote_domain_service.get_daily_quote(
        organization_id=ORG_ID
    )

    assert quote == custom_quote
    motivation_quote_domain_service.quote_repository.get_active_system_quote.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_daily_quote_falls_back_to_system_quote(
    motivation_quote_domain_service,
):
    system_quote = make_quote(
        id=2,
        uuid="system-quote-uuid",
        organization_id=None,
        is_sys_default=True,
    )

    motivation_quote_domain_service.config_repository.get_by_organization_id = (
        AsyncMock(return_value=None)
    )
    motivation_quote_domain_service.quote_repository.get_active_custom_quote = (
        AsyncMock(return_value=None)
    )
    motivation_quote_domain_service.quote_repository.get_active_system_quote = (
        AsyncMock(return_value=system_quote)
    )

    quote = await motivation_quote_domain_service.get_daily_quote(
        organization_id=ORG_ID
    )

    assert quote == system_quote
