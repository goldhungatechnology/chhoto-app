from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
    InvitationStatus,
)

INVITATION_TTL = timedelta(days=7)


def _make_invitation(**overrides) -> InvitationEntity:
    data = {
        "id": 1,
        "organization_id": 10,
        "email": "user@example.com",
        "role_id": 5,
        "team_id": None,
        "invited_by_id": 42,
        "hashed_token": "abc123hash",
        "status": InvitationStatus.PENDING,
        "expires_at": datetime.now(UTC) + INVITATION_TTL,
        "accepted_at": None,
        "created_by_id": 42,
    }
    data.update(overrides)
    return InvitationEntity(**data)


@pytest_asyncio.fixture
async def invitation_domain_service():
    from unittest.mock import Mock

    from src.modules.workforce.domain.services.invitation.invitation_domain_service import (
        InvitationDomainService,
    )

    mock_repo = AsyncMock()
    mock_token_service = Mock()
    mock_token_service.generate_raw = Mock(return_value="raw_token_xyz")
    mock_token_service.hash = Mock(side_effect=lambda r: f"hashed_{r}")
    return InvitationDomainService(
        repository=mock_repo, token_service=mock_token_service
    )


@pytest_asyncio.fixture
async def domain_service_with_token(invitation_domain_service):
    return invitation_domain_service


# ----------------------------- create_invitation -----------------------------


@pytest.mark.asyncio
async def test_create_invitation_success(invitation_domain_service):
    persisted = _make_invitation(id=99, hashed_token="hashed_raw_token_xyz")

    invitation_domain_service.repository.get_by = AsyncMock(return_value=None)
    invitation_domain_service.repository.add = AsyncMock(return_value=persisted)

    result, raw_token = await invitation_domain_service.create_invitation(
        organization_id=10,
        email="  User@Example.COM  ",
        role_id=5,
        team_id=None,
        invited_by_id=42,
    )

    assert result.id == 99
    assert raw_token == "raw_token_xyz"
    assert result.email == "user@example.com"

    events = result.pull_events()
    assert len(events) == 1
    assert events[0].invitation_id == 99
    assert events[0].organization_id == 10
    assert events[0].raw_token == "raw_token_xyz"

    invitation_domain_service.repository.get_by.assert_awaited_once()
    invitation_domain_service.repository.add.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_invitation_revokes_existing_pending(invitation_domain_service):
    existing = _make_invitation(id=5, email="user@example.com")
    persisted = _make_invitation(id=99, hashed_token="hashed_raw_token_xyz")

    invitation_domain_service.repository.get_by = AsyncMock(return_value=existing)
    invitation_domain_service.repository.add = AsyncMock(return_value=persisted)
    invitation_domain_service.repository.update = AsyncMock(return_value=existing)

    result, raw_token = await invitation_domain_service.create_invitation(
        organization_id=10,
        email="user@example.com",
        role_id=5,
        team_id=None,
        invited_by_id=42,
    )

    assert result.id == 99
    assert existing.status == InvitationStatus.REVOKED
    invitation_domain_service.repository.update.assert_awaited_once_with(existing)


@pytest.mark.asyncio
async def test_create_invitation_add_fails_raises_server_error(
    invitation_domain_service,
):
    invitation_domain_service.repository.get_by = AsyncMock(return_value=None)
    invitation_domain_service.repository.add = AsyncMock(return_value=None)

    from src.shared.exceptions.base_exceptions import ServerError

    with pytest.raises(ServerError):
        await invitation_domain_service.create_invitation(
            organization_id=10,
            email="user@example.com",
            role_id=5,
            team_id=None,
            invited_by_id=42,
        )


@pytest.mark.asyncio
async def test_create_invitation_reraises_domain_error(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import DomainError

    invitation_domain_service.repository.get_by = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    with pytest.raises(DomainError):
        await invitation_domain_service.create_invitation(
            organization_id=10,
            email="user@example.com",
            role_id=5,
            team_id=None,
            invited_by_id=42,
        )


@pytest.mark.asyncio
async def test_create_invitation_wraps_unexpected_error(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import ServerError

    invitation_domain_service.repository.get_by = AsyncMock(
        side_effect=ValueError("boom")
    )

    with pytest.raises(ServerError):
        await invitation_domain_service.create_invitation(
            organization_id=10,
            email="user@example.com",
            role_id=5,
            team_id=None,
            invited_by_id=42,
        )


# ----------------------------- get_by_raw_token -----------------------------


@pytest.mark.asyncio
async def test_get_by_raw_token_returns_invitation(invitation_domain_service):
    invitation = _make_invitation()
    invitation_domain_service.repository.get_by_hashed_token = AsyncMock(
        return_value=invitation
    )

    result = await invitation_domain_service.get_by_raw_token("raw_token")

    assert result is invitation
    invitation_domain_service.repository.get_by_hashed_token.assert_awaited_once_with(
        "hashed_raw_token"
    )


@pytest.mark.asyncio
async def test_get_by_raw_token_empty_raises_not_found(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        await invitation_domain_service.get_by_raw_token("")


@pytest.mark.asyncio
async def test_get_by_raw_token_not_found_raises_not_found(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import NotFoundError

    invitation_domain_service.repository.get_by_hashed_token = AsyncMock(
        return_value=None
    )

    with pytest.raises(NotFoundError):
        await invitation_domain_service.get_by_raw_token("nonexistent")


# ----------------------------- get_by_uuid -----------------------------


@pytest.mark.asyncio
async def test_get_by_uuid_returns_invitation(invitation_domain_service):
    invitation = _make_invitation()
    invitation_domain_service.repository.get_by_uuid = AsyncMock(
        return_value=invitation
    )

    result = await invitation_domain_service.get_by_uuid("abc-uuid")

    assert result is invitation


@pytest.mark.asyncio
async def test_get_by_uuid_not_found_raises_not_found(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import NotFoundError

    invitation_domain_service.repository.get_by_uuid = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await invitation_domain_service.get_by_uuid("missing")


# ----------------------------- list_for_organization -----------------------------


@pytest.mark.asyncio
async def test_list_for_organization_returns_all(invitation_domain_service):
    invitations = [_make_invitation(id=1), _make_invitation(id=2)]
    invitation_domain_service.repository.filter = AsyncMock(return_value=invitations)

    result = await invitation_domain_service.list_for_organization()

    assert result == invitations
    invitation_domain_service.repository.filter.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_for_organization_filters_by_status(invitation_domain_service):
    invitations = [_make_invitation(id=1, status=InvitationStatus.PENDING)]
    invitation_domain_service.repository.filter = AsyncMock(return_value=invitations)

    result = await invitation_domain_service.list_for_organization(
        status=InvitationStatus.PENDING
    )

    assert result == invitations
    invitation_domain_service.repository.filter.assert_awaited_once_with(
        status=InvitationStatus.PENDING
    )


@pytest.mark.asyncio
async def test_list_for_organization_invalid_status_raises(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import InvalidError

    with pytest.raises(InvalidError):
        await invitation_domain_service.list_for_organization(status="bogus")


@pytest.mark.asyncio
async def test_list_for_organization_wraps_unexpected_error(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import ServerError

    invitation_domain_service.repository.filter = AsyncMock(
        side_effect=RuntimeError("db")
    )

    with pytest.raises(ServerError):
        await invitation_domain_service.list_for_organization()


# ----------------------------- ensure_acceptable -----------------------------


@pytest.mark.parametrize(
    ("status", "expires_delta", "email", "expected_error"),
    [
        (
            InvitationStatus.REVOKED,
            timedelta(days=1),
            "user@example.com",
            "Invitation has been revoked",
        ),
        (
            InvitationStatus.ACCEPTED,
            timedelta(days=1),
            "user@example.com",
            "Invitation has already been accepted",
        ),
        (
            InvitationStatus.EXPIRED,
            timedelta(days=1),
            "user@example.com",
            "Invitation has expired",
        ),
        (
            InvitationStatus.PENDING,
            timedelta(days=-1),
            "user@example.com",
            "Invitation has expired",
        ),
        (
            InvitationStatus.PENDING,
            timedelta(days=1),
            "other@example.com",
            "different email address",
        ),
    ],
)
def test_ensure_acceptable_fails(
    invitation_domain_service, status, expires_delta, email, expected_error
):
    from src.shared.exceptions.base_exceptions import ConflictError, InvalidError

    inv = _make_invitation(
        status=status,
        expires_at=datetime.now(UTC) + expires_delta,
    )

    with pytest.raises((InvalidError, ConflictError)) as exc_info:
        invitation_domain_service.ensure_acceptable(inv, accepting_email=email)
    assert expected_error in str(exc_info.value)


def test_ensure_acceptable_succeeds(invitation_domain_service):
    inv = _make_invitation(
        status=InvitationStatus.PENDING,
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )

    invitation_domain_service.ensure_acceptable(inv, accepting_email="user@example.com")


# ----------------------------- mark_as_accepted -----------------------------


@pytest.mark.asyncio
async def test_mark_as_accepted_success(invitation_domain_service):
    invitation = _make_invitation()
    accepted = _make_invitation(
        status=InvitationStatus.ACCEPTED, accepted_at=datetime.now(UTC)
    )
    # Acceptance is an atomic compare-and-set in the repository.
    invitation_domain_service.repository.mark_accepted_if_pending = AsyncMock(
        return_value=accepted
    )

    result = await invitation_domain_service.mark_as_accepted(invitation)

    assert result.status == InvitationStatus.ACCEPTED
    assert result.accepted_at is not None
    invitation_domain_service.repository.mark_accepted_if_pending.assert_awaited_once_with(
        invitation.id
    )


@pytest.mark.asyncio
async def test_mark_as_accepted_already_accepted_raises_conflict(
    invitation_domain_service,
):
    invitation = _make_invitation()
    # No row updated -> already accepted / not pending.
    invitation_domain_service.repository.mark_accepted_if_pending = AsyncMock(
        return_value=None
    )

    from src.shared.exceptions.base_exceptions import ConflictError

    with pytest.raises(ConflictError):
        await invitation_domain_service.mark_as_accepted(invitation)


@pytest.mark.asyncio
async def test_mark_as_accepted_reraises_domain_error(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import DomainError

    invitation_domain_service.repository.mark_accepted_if_pending = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    with pytest.raises(DomainError):
        await invitation_domain_service.mark_as_accepted(_make_invitation())


# ----------------------------- revoke -----------------------------


@pytest.mark.asyncio
async def test_revoke_pending_invitation_success(invitation_domain_service):
    invitation = _make_invitation(id=1, status=InvitationStatus.PENDING)
    invitation_domain_service.repository.get_by_uuid = AsyncMock(
        return_value=invitation
    )
    invitation_domain_service.repository.update = AsyncMock(side_effect=lambda e: e)

    result = await invitation_domain_service.revoke("uuid-abc")

    assert result.status == InvitationStatus.REVOKED
    events = result.pull_events()
    assert len(events) == 1
    assert events[0].invitation_id == 1
    assert events[0].organization_id == 10


@pytest.mark.asyncio
async def test_revoke_already_revoked_is_idempotent(invitation_domain_service):
    invitation = _make_invitation(id=1, status=InvitationStatus.REVOKED)
    invitation_domain_service.repository.get_by_uuid = AsyncMock(
        return_value=invitation
    )

    result = await invitation_domain_service.revoke("uuid-abc")

    assert result is invitation
    events = result.pull_events()
    assert len(events) == 0


@pytest.mark.asyncio
async def test_revoke_accepted_raises_conflict(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import ConflictError

    invitation = _make_invitation(id=1, status=InvitationStatus.ACCEPTED)
    invitation_domain_service.repository.get_by_uuid = AsyncMock(
        return_value=invitation
    )

    with pytest.raises(ConflictError):
        await invitation_domain_service.revoke("uuid-abc")


@pytest.mark.asyncio
async def test_revoke_not_found_raises_not_found(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import NotFoundError

    invitation_domain_service.repository.get_by_uuid = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await invitation_domain_service.revoke("missing")


@pytest.mark.asyncio
async def test_revoke_update_fails_raises_server_error(invitation_domain_service):
    invitation = _make_invitation(id=1, status=InvitationStatus.PENDING)
    invitation_domain_service.repository.get_by_uuid = AsyncMock(
        return_value=invitation
    )
    invitation_domain_service.repository.update = AsyncMock(return_value=None)

    from src.shared.exceptions.base_exceptions import ServerError

    with pytest.raises(ServerError):
        await invitation_domain_service.revoke("uuid-abc")


# ----------------------------- resend -----------------------------


@pytest.mark.asyncio
async def test_resend_pending_invitation_success(invitation_domain_service):
    old = _make_invitation(id=1, email="user@example.com")
    new = _make_invitation(id=99, hashed_token="hashed_new_token")

    invitation_domain_service.repository.get_by_uuid = AsyncMock(return_value=old)
    invitation_domain_service.repository.update = AsyncMock(side_effect=lambda e: e)
    invitation_domain_service.repository.get_by = AsyncMock(return_value=None)
    invitation_domain_service.repository.add = AsyncMock(return_value=new)

    result, raw_token = await invitation_domain_service.resend("uuid-abc", actor_id=42)

    assert result.id == 99
    assert raw_token == "raw_token_xyz"
    assert old.status == InvitationStatus.REVOKED

    events = result.pull_events()
    assert len(events) == 1
    assert events[0].old_invitation_id == 1
    assert events[0].new_invitation_id == 99


@pytest.mark.asyncio
async def test_resend_accepted_raises_conflict(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import ConflictError

    old = _make_invitation(id=1, status=InvitationStatus.ACCEPTED)
    invitation_domain_service.repository.get_by_uuid = AsyncMock(return_value=old)

    with pytest.raises(ConflictError):
        await invitation_domain_service.resend("uuid-abc", actor_id=42)


@pytest.mark.asyncio
async def test_resend_revoked_creates_fresh(invitation_domain_service):
    old = _make_invitation(
        id=1, status=InvitationStatus.REVOKED, email="user@example.com"
    )
    new = _make_invitation(id=99, hashed_token="hashed_new_token")

    invitation_domain_service.repository.get_by_uuid = AsyncMock(return_value=old)
    invitation_domain_service.repository.get_by = AsyncMock(return_value=None)
    invitation_domain_service.repository.add = AsyncMock(return_value=new)

    result, raw_token = await invitation_domain_service.resend("uuid-abc", actor_id=42)

    assert result.id == 99
    assert raw_token == "raw_token_xyz"


@pytest.mark.asyncio
async def test_resend_new_invite_fails_raises_server_error(invitation_domain_service):
    from src.shared.exceptions.base_exceptions import ServerError

    old = _make_invitation(id=1, email="user@example.com")

    invitation_domain_service.repository.get_by_uuid = AsyncMock(return_value=old)
    invitation_domain_service.repository.get_by = AsyncMock(return_value=None)
    invitation_domain_service.repository.add = AsyncMock(return_value=None)

    with pytest.raises(ServerError):
        await invitation_domain_service.resend("uuid-abc", actor_id=42)
