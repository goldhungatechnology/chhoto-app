from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


def _make_team_member(**overrides):
    from src.modules.workforce.domain.entities.team.team_member_entity import (
        TeamMemberEntity,
    )

    data = {
        "id": 1,
        "team_id": 10,
        "member_id": 20,
        "role": "member",
        "created_by_id": 7,
    }
    data.update(overrides)
    return TeamMemberEntity(**data)


@pytest_asyncio.fixture
async def team_member_domain_service():
    from src.modules.workforce.domain.services.team.team_member_domain_service import (
        TeamMemberDomainService,
    )

    mock_repo = AsyncMock()
    return TeamMemberDomainService(repository=mock_repo)


# ----------------------------- add_team_member -----------------------------


@pytest.mark.asyncio
async def test_add_team_member_success(team_member_domain_service):
    from src.modules.workforce.domain.events.team.team_domain_events import (
        TeamMemberAddedEvent,
    )

    persisted = _make_team_member(id=55)

    team_member_domain_service.repository.get_by = AsyncMock(return_value=None)
    team_member_domain_service.repository.add = AsyncMock(return_value=persisted)

    result = await team_member_domain_service.add_team_member(
        _make_team_member(id=None), organization_id=10
    )

    assert result.id == 55
    events = result.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], TeamMemberAddedEvent)
    assert events[0].team_id == 10
    assert events[0].member_id == 20


@pytest.mark.asyncio
async def test_add_team_member_duplicate_raises_conflict(team_member_domain_service):
    from src.shared.exceptions.base_exceptions import ConflictError

    team_member_domain_service.repository.get_by = AsyncMock(
        return_value=_make_team_member()
    )

    with pytest.raises(ConflictError):
        await team_member_domain_service.add_team_member(
            _make_team_member(id=None), organization_id=10
        )


@pytest.mark.asyncio
async def test_add_team_member_repository_returns_invalid_raises_server_error(
    team_member_domain_service,
):
    from src.shared.exceptions.base_exceptions import ServerError

    team_member_domain_service.repository.get_by = AsyncMock(return_value=None)
    team_member_domain_service.repository.add = AsyncMock(
        return_value=_make_team_member(id=None)
    )

    with pytest.raises(ServerError):
        await team_member_domain_service.add_team_member(
            _make_team_member(id=None), organization_id=10
        )


# ----------------------------- list_team_members -----------------------------


@pytest.mark.asyncio
async def test_list_team_members_delegates_to_repository(team_member_domain_service):
    members = [_make_team_member(id=1), _make_team_member(id=2, member_id=21)]
    team_member_domain_service.repository.list_by_team_id = AsyncMock(
        return_value=members
    )

    result = await team_member_domain_service.list_team_members(team_id=10)

    assert result == members
    team_member_domain_service.repository.list_by_team_id.assert_awaited_once_with(10)


@pytest.mark.asyncio
async def test_list_team_members_wraps_unexpected_error(team_member_domain_service):
    from src.shared.exceptions.base_exceptions import ServerError

    team_member_domain_service.repository.list_by_team_id = AsyncMock(
        side_effect=RuntimeError("db")
    )

    with pytest.raises(ServerError):
        await team_member_domain_service.list_team_members(team_id=10)


# ----------------------------- list_members_by_team_ids -----------------------------


@pytest.mark.asyncio
async def test_list_members_by_team_ids_delegates_to_repository(
    team_member_domain_service,
):
    members = [
        _make_team_member(id=1, team_id=10, role="team_lead"),
        _make_team_member(id=2, team_id=11, member_id=21, role="member"),
    ]
    team_member_domain_service.repository.list_by_team_ids = AsyncMock(
        return_value=members
    )

    result = await team_member_domain_service.list_members_by_team_ids([10, 11])

    assert result == members
    team_member_domain_service.repository.list_by_team_ids.assert_awaited_once_with(
        [10, 11]
    )


@pytest.mark.asyncio
async def test_list_members_by_team_ids_wraps_unexpected_error(
    team_member_domain_service,
):
    from src.shared.exceptions.base_exceptions import ServerError

    team_member_domain_service.repository.list_by_team_ids = AsyncMock(
        side_effect=RuntimeError("db")
    )

    with pytest.raises(ServerError):
        await team_member_domain_service.list_members_by_team_ids([10])


# ----------------------------- remove_team_member -----------------------------


@pytest.mark.asyncio
async def test_remove_team_member_deletes_when_found(team_member_domain_service):
    existing = _make_team_member(id=55)
    team_member_domain_service.repository.get_by = AsyncMock(return_value=existing)
    team_member_domain_service.repository.delete = AsyncMock()

    await team_member_domain_service.remove_team_member(
        team_id=10, member_id=20, organization_id=10
    )

    team_member_domain_service.repository.delete.assert_awaited_once_with(
        55, audit=False
    )


@pytest.mark.asyncio
async def test_remove_team_member_not_found_raises_not_found(
    team_member_domain_service,
):
    from src.shared.exceptions.base_exceptions import NotFoundError

    team_member_domain_service.repository.get_by = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await team_member_domain_service.remove_team_member(
            team_id=10, member_id=20, organization_id=10
        )


@pytest.mark.asyncio
async def test_remove_team_member_lead_raises_conflict(team_member_domain_service):
    from src.shared.exceptions.base_exceptions import ConflictError

    existing = _make_team_member(id=55, role="team_lead")
    team_member_domain_service.repository.get_by = AsyncMock(return_value=existing)
    team_member_domain_service.repository.delete = AsyncMock()

    with pytest.raises(ConflictError):
        await team_member_domain_service.remove_team_member(
            team_id=10, member_id=20, organization_id=10
        )

    # The lead is never deleted; the caller must reassign the lead first.
    team_member_domain_service.repository.delete.assert_not_called()


# ----------------------------- set_member_role -----------------------------


@pytest.mark.asyncio
async def test_set_member_role_promotes_and_emits_event(team_member_domain_service):
    from src.modules.workforce.domain.events.team.team_domain_events import (
        TeamMemberRoleAssignedEvent,
    )

    existing = _make_team_member(id=55, role="member")
    team_member_domain_service.repository.get_by = AsyncMock(return_value=existing)
    team_member_domain_service.repository.update = AsyncMock(
        side_effect=lambda e, **kw: e
    )

    result = await team_member_domain_service.set_member_role(
        team_id=10, member_id=20, organization_id=10, role="team_lead", actor_id=7
    )

    assert result.role == "team_lead"
    assert result.is_team_lead is True
    assert result.updated_by_id == 7
    events = result.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], TeamMemberRoleAssignedEvent)
    assert events[0].role == "team_lead"


@pytest.mark.asyncio
async def test_set_member_role_supervisor(team_member_domain_service):
    existing = _make_team_member(id=55, role="member")
    team_member_domain_service.repository.get_by = AsyncMock(return_value=existing)
    team_member_domain_service.repository.update = AsyncMock(
        side_effect=lambda e, **kw: e
    )

    result = await team_member_domain_service.set_member_role(
        team_id=10, member_id=20, organization_id=10, role="supervisor"
    )

    assert result.role == "supervisor"
    assert result.is_team_lead is False


@pytest.mark.asyncio
async def test_set_member_role_same_role_is_idempotent(team_member_domain_service):
    existing = _make_team_member(role="team_lead")
    team_member_domain_service.repository.get_by = AsyncMock(return_value=existing)

    result = await team_member_domain_service.set_member_role(
        team_id=10, member_id=20, organization_id=10, role="team_lead"
    )

    assert result is existing
    # No update call when the role is unchanged
    team_member_domain_service.repository.update.assert_not_called()
    # No event emitted either
    assert result.pull_events() == []


@pytest.mark.asyncio
async def test_set_member_role_invalid_role_raises_invalid(team_member_domain_service):
    from src.shared.exceptions.base_exceptions import InvalidError

    with pytest.raises(InvalidError):
        await team_member_domain_service.set_member_role(
            team_id=10, member_id=20, organization_id=10, role="bogus"
        )


@pytest.mark.asyncio
async def test_set_member_role_not_found_raises_not_found(team_member_domain_service):
    from src.shared.exceptions.base_exceptions import NotFoundError

    team_member_domain_service.repository.get_by = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await team_member_domain_service.set_member_role(
            team_id=10, member_id=20, organization_id=10, role="team_lead"
        )
