from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def daily_motivation_config_domain_service():
    from src.modules.motivation.domain.services.daily_motivation_config_domain_service import (
        DailyMotivationConfigDomainService,
    )

    mock_repo = AsyncMock()
    mock_repo.session = None
    mock_repo.get_by_organization_id = AsyncMock()
    mock_repo.add = AsyncMock()
    mock_repo.update = AsyncMock()

    return DailyMotivationConfigDomainService(repository=mock_repo)


@pytest.mark.asyncio
async def test_create_config_with_existing_config_raises_conflict(
    daily_motivation_config_domain_service,
):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )
    from src.shared.exceptions.base_exceptions import ConflictError

    daily_motivation_config_domain_service.repository.get_by_organization_id = (
        AsyncMock(
            return_value=DailyMotivationConfigEntity(
                id=1,
                organization_id=1,
                is_enabled=True,
                allow_reactions=True,
            )
        )
    )

    with pytest.raises(ConflictError):
        await daily_motivation_config_domain_service.create_config(
            config_entity=DailyMotivationConfigEntity(
                organization_id=1,
                is_enabled=True,
                allow_reactions=True,
            ),
            actor_id=1,
        )


@pytest.mark.asyncio
async def test_create_config_success(daily_motivation_config_domain_service):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    config = DailyMotivationConfigEntity(
        id=1,
        organization_id=1,
        is_enabled=True,
        allow_reactions=True,
    )

    daily_motivation_config_domain_service.repository.get_by_organization_id = (
        AsyncMock(return_value=None)
    )
    daily_motivation_config_domain_service.repository.add = AsyncMock(
        return_value=config
    )

    created = await daily_motivation_config_domain_service.create_config(
        config_entity=config,
        actor_id=1,
    )

    assert created == config
    assert created.created_by_id == 1


@pytest.mark.asyncio
async def test_get_config_by_organization_id_success(
    daily_motivation_config_domain_service,
):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    existing_config = DailyMotivationConfigEntity(
        id=1,
        organization_id=1,
        is_enabled=True,
        allow_reactions=True,
    )

    daily_motivation_config_domain_service.repository.get_by_organization_id = (
        AsyncMock(return_value=existing_config)
    )

    config = await daily_motivation_config_domain_service.get_config_by_organization_id(
        organization_id=1,
    )

    assert config == existing_config


@pytest.mark.asyncio
async def test_get_or_create_default_config_returns_existing_config(
    daily_motivation_config_domain_service,
):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    existing_config = DailyMotivationConfigEntity(
        id=1,
        organization_id=1,
        is_enabled=True,
        allow_reactions=True,
    )

    daily_motivation_config_domain_service.repository.get_by_organization_id = (
        AsyncMock(return_value=existing_config)
    )

    config = await daily_motivation_config_domain_service.get_or_create_default_config(
        organization_id=1,
        actor_id=1,
    )

    assert config == existing_config


@pytest.mark.asyncio
async def test_get_or_create_default_config_creates_default_when_missing(
    daily_motivation_config_domain_service,
):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    created_config = DailyMotivationConfigEntity(
        id=1,
        organization_id=1,
        sys_quote_source=True,
        is_enabled=True,
        allow_reactions=True,
        created_by_id=1,
    )

    daily_motivation_config_domain_service.repository.get_by_organization_id = (
        AsyncMock(return_value=None)
    )
    daily_motivation_config_domain_service.repository.add = AsyncMock(
        return_value=created_config
    )

    config = await daily_motivation_config_domain_service.get_or_create_default_config(
        organization_id=1,
        actor_id=1,
    )

    assert config.organization_id == 1
    assert config.sys_quote_source is True
    assert config.is_enabled is True
    assert config.allow_reactions is True
    assert config.created_by_id == 1


@pytest.mark.asyncio
async def test_update_config_not_found_raises_invalid_error(
    daily_motivation_config_domain_service,
):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )
    from src.shared.exceptions.base_exceptions import InvalidError

    daily_motivation_config_domain_service.repository.get_by_organization_id = (
        AsyncMock(return_value=None)
    )

    with pytest.raises(InvalidError):
        await daily_motivation_config_domain_service.update_config(
            config_entity=DailyMotivationConfigEntity(
                organization_id=1,
                is_enabled=False,
                allow_reactions=False,
            ),
            actor_id=1,
        )


@pytest.mark.asyncio
async def test_update_config_success(daily_motivation_config_domain_service):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    existing_config = DailyMotivationConfigEntity(
        id=1,
        organization_id=1,
        sys_quote_source=True,
        is_enabled=True,
        allow_reactions=True,
    )

    daily_motivation_config_domain_service.repository.get_by_organization_id = (
        AsyncMock(return_value=existing_config)
    )
    daily_motivation_config_domain_service.repository.update = AsyncMock(
        return_value=existing_config
    )

    updated = await daily_motivation_config_domain_service.update_config(
        config_entity=DailyMotivationConfigEntity(
            organization_id=1,
            sys_quote_source=False,
            is_enabled=False,
            allow_reactions=False,
        ),
        actor_id=1,
    )

    assert updated.sys_quote_source is False
    assert updated.is_enabled is False
    assert updated.allow_reactions is False
    assert updated.updated_by_id == 1


@pytest.mark.asyncio
async def test_reset_config_success(daily_motivation_config_domain_service):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    existing_config = DailyMotivationConfigEntity(
        id=1,
        organization_id=1,
        sys_quote_source=False,
        is_enabled=False,
        allow_reactions=False,
    )

    daily_motivation_config_domain_service.repository.get_by_organization_id = (
        AsyncMock(return_value=existing_config)
    )
    daily_motivation_config_domain_service.repository.update = AsyncMock(
        return_value=existing_config
    )

    reset_config = await daily_motivation_config_domain_service.reset_config(
        organization_id=1,
        actor_id=1,
    )

    assert reset_config.sys_quote_source is True
    assert reset_config.is_enabled is True
    assert reset_config.allow_reactions is True
    assert reset_config.updated_by_id == 1


@pytest.mark.asyncio
async def test_reset_config_creates_default_when_config_not_found(
    daily_motivation_config_domain_service,
):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    created_config = DailyMotivationConfigEntity(
        id=1,
        organization_id=1,
        sys_quote_source=True,
        is_enabled=True,
        allow_reactions=True,
        created_by_id=1,
    )

    daily_motivation_config_domain_service.repository.get_by_organization_id = (
        AsyncMock(return_value=None)
    )
    daily_motivation_config_domain_service.repository.add = AsyncMock(
        return_value=created_config
    )

    reset_config = await daily_motivation_config_domain_service.reset_config(
        organization_id=1,
        actor_id=1,
    )

    assert reset_config.organization_id == 1
    assert reset_config.sys_quote_source is True
    assert reset_config.is_enabled is True
    assert reset_config.allow_reactions is True
    assert reset_config.created_by_id == 1
