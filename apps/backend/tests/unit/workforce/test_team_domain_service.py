from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


def _make_team(**overrides):
    from src.modules.workforce.domain.entities.team.team_entity import TeamEntity

    data = {
        "id": 1,
        "name": "Engineering",
        "description": "Builds the product",
        "color": "#ff0000",
        "timezone": "UTC",
        "is_default": False,
        "organization_id": 10,
        "created_by_id": 42,
    }
    data.update(overrides)
    return TeamEntity(**data)


@pytest_asyncio.fixture
async def team_domain_service():
    from src.modules.workforce.domain.services.team.team_domain_service import (
        TeamDomainService,
    )

    mock_repo = AsyncMock()
    return TeamDomainService(repository=mock_repo)


# ----------------------------- create_team -----------------------------


@pytest.mark.asyncio
async def test_create_team_success(team_domain_service):
    from src.modules.workforce.domain.events.team.team_domain_events import (
        TeamCreatedEvent,
    )

    team = _make_team(id=None)
    persisted = _make_team(id=99)

    team_domain_service.repository.get_by = AsyncMock(return_value=None)
    team_domain_service.repository.add = AsyncMock(return_value=persisted)

    created = await team_domain_service.create_team(team)

    assert created.id == 99
    events = created.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], TeamCreatedEvent)
    assert events[0].team_id == 99
    assert events[0].organization_id == 10
    assert events[0].name == "Engineering"


@pytest.mark.asyncio
async def test_create_team_duplicate_name_raises_conflict(team_domain_service):
    from src.shared.exceptions.base_exceptions import ConflictError

    team_domain_service.repository.get_by = AsyncMock(return_value=_make_team())

    with pytest.raises(ConflictError):
        await team_domain_service.create_team(_make_team(id=None))


@pytest.mark.asyncio
async def test_create_team_when_default_already_exists_raises_conflict(
    team_domain_service,
):
    from src.shared.exceptions.base_exceptions import ConflictError

    team_domain_service.repository.get_by = AsyncMock(
        side_effect=[None, _make_team(is_default=True)]
    )

    with pytest.raises(ConflictError):
        await team_domain_service.create_team(_make_team(id=None, is_default=True))


@pytest.mark.asyncio
async def test_create_team_returns_invalid_entity_raises_server_error(
    team_domain_service,
):
    from src.shared.exceptions.base_exceptions import ServerError

    team_domain_service.repository.get_by = AsyncMock(return_value=None)
    team_domain_service.repository.add = AsyncMock(return_value=_make_team(id=None))

    with pytest.raises(ServerError):
        await team_domain_service.create_team(_make_team(id=None))


@pytest.mark.asyncio
async def test_create_team_wraps_unexpected_error_in_server_error(team_domain_service):
    from src.shared.exceptions.base_exceptions import ServerError

    team_domain_service.repository.get_by = AsyncMock(side_effect=ValueError("boom"))

    with pytest.raises(ServerError):
        await team_domain_service.create_team(_make_team(id=None))


# ----------------------------- get_team_by_uuid -----------------------------


@pytest.mark.asyncio
async def test_get_team_by_uuid_returns_active_team(team_domain_service):
    team = _make_team()
    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=team)

    result = await team_domain_service.get_team_by_uuid("abc")

    assert result is team
    team_domain_service.repository.get_by_uuid.assert_awaited_once_with("abc")


@pytest.mark.asyncio
async def test_get_team_by_uuid_missing_raises_not_found(team_domain_service):
    from src.shared.exceptions.base_exceptions import NotFoundError

    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await team_domain_service.get_team_by_uuid("missing")


@pytest.mark.asyncio
async def test_get_team_by_uuid_soft_deleted_raises_not_found(team_domain_service):
    from datetime import UTC, datetime

    from src.shared.exceptions.base_exceptions import NotFoundError

    team_domain_service.repository.get_by_uuid = AsyncMock(
        return_value=_make_team(deleted_at=datetime.now(UTC))
    )

    with pytest.raises(NotFoundError):
        await team_domain_service.get_team_by_uuid("abc")


# ----------------------------- list_teams -----------------------------


@pytest.mark.asyncio
async def test_list_teams_returns_paginated_teams_and_total(team_domain_service):
    teams = [_make_team(id=1), _make_team(id=2, name="Sales")]
    team_domain_service.repository.list_paginated = AsyncMock(return_value=(teams, 2))

    result, total = await team_domain_service.list_teams_by_organization_id(
        status="active", limit=20, offset=0
    )

    assert result == teams
    assert total == 2
    team_domain_service.repository.list_paginated.assert_awaited_once_with(
        status="active", limit=20, offset=0
    )


@pytest.mark.asyncio
async def test_list_teams_uses_default_pagination(team_domain_service):
    team_domain_service.repository.list_paginated = AsyncMock(return_value=([], 0))

    result, total = await team_domain_service.list_teams_by_organization_id()

    assert result == []
    assert total == 0
    team_domain_service.repository.list_paginated.assert_awaited_once_with(
        status=None, limit=50, offset=0
    )


@pytest.mark.asyncio
async def test_list_teams_wraps_unexpected_error(team_domain_service):
    from src.shared.exceptions.base_exceptions import ServerError

    team_domain_service.repository.list_paginated = AsyncMock(
        side_effect=RuntimeError("db")
    )

    with pytest.raises(ServerError):
        await team_domain_service.list_teams_by_organization_id()


# ----------------------------- update_team -----------------------------


@pytest.mark.asyncio
async def test_update_team_renames_and_emits_event(team_domain_service):
    from src.modules.workforce.domain.events.team.team_domain_events import (
        TeamUpdatedEvent,
    )

    existing = _make_team(name="OldName")
    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=existing)
    team_domain_service.repository.get_by = AsyncMock(return_value=None)
    team_domain_service.repository.update = AsyncMock(side_effect=lambda e: e)

    updated = await team_domain_service.update_team(
        team_uuid="abc",
        name="NewName",
        description="new desc",
        actor_id=7,
    )

    assert updated.name == "NewName"
    assert updated.description == "new desc"
    assert updated.updated_by_id == 7
    assert updated.updated_at is not None

    events = updated.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], TeamUpdatedEvent)


@pytest.mark.asyncio
async def test_update_team_duplicate_name_raises_conflict(team_domain_service):
    from src.shared.exceptions.base_exceptions import ConflictError

    existing = _make_team(id=1, name="Engineering")
    conflicting = _make_team(id=2, name="Sales")

    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=existing)
    team_domain_service.repository.get_by = AsyncMock(return_value=conflicting)

    with pytest.raises(ConflictError):
        await team_domain_service.update_team(team_uuid="abc", name="Sales")


@pytest.mark.asyncio
async def test_update_team_set_default_when_another_default_exists(team_domain_service):
    from src.shared.exceptions.base_exceptions import ConflictError

    existing = _make_team(id=1, is_default=False)
    other_default = _make_team(id=2, name="General", is_default=True)

    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=existing)
    team_domain_service.repository.get_by = AsyncMock(return_value=other_default)

    with pytest.raises(ConflictError):
        await team_domain_service.update_team(team_uuid="abc", is_default=True)


@pytest.mark.asyncio
async def test_update_team_marks_default_when_no_conflict(team_domain_service):
    existing = _make_team(id=1, is_default=False)

    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=existing)
    team_domain_service.repository.get_by = AsyncMock(return_value=None)
    team_domain_service.repository.update = AsyncMock(side_effect=lambda e: e)

    updated = await team_domain_service.update_team(team_uuid="abc", is_default=True)

    assert updated.is_default is True


@pytest.mark.asyncio
async def test_update_team_unmarks_default(team_domain_service):
    existing = _make_team(id=1, is_default=True)

    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=existing)
    team_domain_service.repository.update = AsyncMock(side_effect=lambda e: e)

    updated = await team_domain_service.update_team(team_uuid="abc", is_default=False)

    assert updated.is_default is False


@pytest.mark.asyncio
async def test_update_team_not_found_raises_not_found(team_domain_service):
    from src.shared.exceptions.base_exceptions import NotFoundError

    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await team_domain_service.update_team(team_uuid="missing", name="x")


# ----------------------------- delete_team -----------------------------


@pytest.mark.asyncio
async def test_delete_team_soft_deletes_and_emits_event(team_domain_service):
    from src.modules.workforce.domain.events.team.team_domain_events import (
        TeamDeletedEvent,
    )

    existing = _make_team(id=1, is_default=False)
    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=existing)
    team_domain_service.repository.update = AsyncMock(side_effect=lambda e: e)

    deleted = await team_domain_service.delete_team(team_uuid="abc")

    assert deleted.deleted_at is not None
    events = deleted.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], TeamDeletedEvent)


@pytest.mark.asyncio
async def test_delete_team_default_raises_conflict(team_domain_service):
    from src.shared.exceptions.base_exceptions import ConflictError

    team_domain_service.repository.get_by_uuid = AsyncMock(
        return_value=_make_team(id=1, is_default=True)
    )

    with pytest.raises(ConflictError):
        await team_domain_service.delete_team(team_uuid="abc")


@pytest.mark.asyncio
async def test_delete_team_not_found_raises_not_found(team_domain_service):
    from src.shared.exceptions.base_exceptions import NotFoundError

    team_domain_service.repository.get_by_uuid = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await team_domain_service.delete_team(team_uuid="missing")
