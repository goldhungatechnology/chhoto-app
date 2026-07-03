from unittest.mock import AsyncMock, patch

import pytest

from src.modules.motivation.application.listeners.motivation_organization_created_listener import (
    on_organization_created_seed_motivation_quotes,
)
from src.modules.organization.domain.events.organization_domain_events import (
    OrganizationCreatedEvent,
)
from src.shared.exceptions.base_exceptions import ServerError


@pytest.mark.asyncio
async def test_on_organization_created_seed_motivation_quotes_raises_server_error_if_no_session():
    event = OrganizationCreatedEvent(
        actor_id=1,
        organization_id=1,
        organization_member_id=1,
        session=None,
    )
    with pytest.raises(ServerError):
        await on_organization_created_seed_motivation_quotes(event)


@pytest.mark.asyncio
@patch(
    "src.modules.motivation.application.listeners.motivation_organization_created_listener.seed_default_quotes_for_organization"
)
async def test_on_organization_created_seed_motivation_quotes_calls_task(
    mock_seed_task,
):
    mock_session = AsyncMock()
    event = OrganizationCreatedEvent(
        actor_id=1,
        organization_id=1,
        organization_member_id=1,
        session=mock_session,
    )
    await on_organization_created_seed_motivation_quotes(event)
    mock_seed_task.assert_called_once_with(
        session=mock_session,
        organization_id=1,
        actor_id=1,
    )
