from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
    InvitationStatus,
)

INVITATION_TTL = timedelta(days=7)


def _entity_without_events() -> Mock:
    """
    A stand-in domain entity whose pull_events() yields nothing, for mocking
    domain-service results that the use case publishes events from.
    """
    return Mock(pull_events=Mock(return_value=[]))


def _make_invitation(**overrides) -> InvitationEntity:
    data = {
        "id": 1,
        "uuid": "inv-uuid-123",
        "organization_id": 10,
        "email": "user@example.com",
        "role_id": 5,
        "team_id": None,
        "invited_by_id": 42,
        "hashed_token": "hashed_raw_token",
        "status": InvitationStatus.PENDING,
        "expires_at": datetime.now(UTC) + INVITATION_TTL,
        "accepted_at": None,
        "created_by_id": 42,
    }
    data.update(overrides)
    return InvitationEntity(**data)


def _make_role(**overrides):
    from src.modules.workforce.domain.entities.rbac.rbac_role_entity import (
        RoleEntity,
    )

    data = {
        "id": 5,
        "uuid": "role-uuid",
        "name": "Admin",
        "description": None,
        "is_system_role": False,
        "organization_id": 10,
    }
    data.update(overrides)
    return RoleEntity(**data)


def _make_team(**overrides):
    from src.modules.workforce.domain.entities.team.team_entity import TeamEntity

    data = {"id": 20, "uuid": "team-uuid", "name": "Engineering", "organization_id": 10}
    data.update(overrides)
    return TeamEntity(**data)


def _make_user(**overrides):
    from src.modules.auth.domain.entities.user_entity import UserEntity

    data = {
        "id": 100,
        "uuid": "user-uuid",
        "username": "testuser",
        "email": "user@example.com",
        "avatar_bg": "#abcdef",
        "status": "active",
        "is_onboarded": True,
        "full_name": "Test User",
    }
    data.update(overrides)
    return UserEntity(**data)


# ----------------------------- CreateInvitationUseCase -----------------------------


@pytest.mark.asyncio
async def test_create_invitation_usecase_success():
    from src.modules.workforce.application.usecases.invitation.create_invitation_usecase import (
        CreateInvitationUseCase,
    )
    from src.modules.workforce.domain.events.invitation.invitation_domain_events import (
        InvitationCreatedEvent,
    )

    role = _make_role()
    team = _make_team()
    created = _make_invitation(id=99)
    created.add_event(
        InvitationCreatedEvent(
            invitation_id=99,
            organization_id=10,
            email="user@example.com",
            raw_token="raw_xyz",
            expires_at=datetime.now(UTC) + INVITATION_TTL,
        )
    )

    mock_role_service = AsyncMock()
    mock_role_service.get_role_by_uuid = AsyncMock(return_value=role)

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    mock_invite_service = AsyncMock()
    mock_invite_service.create_invitation = AsyncMock(return_value=(created, "raw_xyz"))

    usecase = CreateInvitationUseCase(
        invitation_domain_service=mock_invite_service,
        rbac_role_domain_service=mock_role_service,
        team_domain_service=mock_team_service,
    )

    with patch(
        "src.modules.workforce.application.usecases.invitation.create_invitation_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result_invite, result_token = await usecase.execute(
            organization_id=10,
            email="user@example.com",
            role_uuid="role-uuid",
            team_uuid="team-uuid",
            actor_id=42,
        )

        assert result_invite.id == 99
        assert result_token == "raw_xyz"
        mediator_mock.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_invitation_usecase_without_team():
    from src.modules.workforce.application.usecases.invitation.create_invitation_usecase import (
        CreateInvitationUseCase,
    )

    role = _make_role()
    created = _make_invitation(id=99)

    mock_role_service = AsyncMock()
    mock_role_service.get_role_by_uuid = AsyncMock(return_value=role)

    mock_invite_service = AsyncMock()
    mock_invite_service.create_invitation = AsyncMock(return_value=(created, "raw_xyz"))

    usecase = CreateInvitationUseCase(
        invitation_domain_service=mock_invite_service,
        rbac_role_domain_service=mock_role_service,
        team_domain_service=AsyncMock(),
    )

    with patch(
        "src.modules.workforce.application.usecases.invitation.create_invitation_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result_invite, result_token = await usecase.execute(
            organization_id=10,
            email="user@example.com",
            role_uuid="role-uuid",
            team_uuid=None,
            actor_id=42,
        )

        assert result_invite.id == 99
        assert result_token == "raw_xyz"


@pytest.mark.asyncio
async def test_create_invitation_usecase_role_not_found_raises_not_found():
    from src.modules.workforce.application.usecases.invitation.create_invitation_usecase import (
        CreateInvitationUseCase,
    )
    from src.shared.exceptions.base_exceptions import NotFoundError

    mock_role_service = AsyncMock()
    mock_role_service.get_role_by_uuid = AsyncMock(return_value=None)

    usecase = CreateInvitationUseCase(
        invitation_domain_service=AsyncMock(),
        rbac_role_domain_service=mock_role_service,
        team_domain_service=AsyncMock(),
    )

    with pytest.raises(NotFoundError):
        await usecase.execute(
            organization_id=10,
            email="user@example.com",
            role_uuid="bad-role",
            team_uuid=None,
            actor_id=42,
        )


@pytest.mark.asyncio
async def test_create_invitation_usecase_reraises_domain_error():
    from src.modules.workforce.application.usecases.invitation.create_invitation_usecase import (
        CreateInvitationUseCase,
    )
    from src.shared.exceptions.base_exceptions import DomainError

    mock_role_service = AsyncMock()
    mock_role_service.get_role_by_uuid = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    usecase = CreateInvitationUseCase(
        invitation_domain_service=AsyncMock(),
        rbac_role_domain_service=mock_role_service,
        team_domain_service=AsyncMock(),
    )

    with pytest.raises(DomainError):
        await usecase.execute(
            organization_id=10,
            email="user@example.com",
            role_uuid="role-uuid",
            team_uuid=None,
            actor_id=42,
        )


@pytest.mark.asyncio
async def test_create_invitation_usecase_wraps_unexpected_error():
    from src.modules.workforce.application.usecases.invitation.create_invitation_usecase import (
        CreateInvitationUseCase,
    )
    from src.shared.exceptions.base_exceptions import CreateError

    mock_role_service = AsyncMock()
    mock_role_service.get_role_by_uuid = AsyncMock(side_effect=ValueError("boom"))

    usecase = CreateInvitationUseCase(
        invitation_domain_service=AsyncMock(),
        rbac_role_domain_service=mock_role_service,
        team_domain_service=AsyncMock(),
    )

    with pytest.raises(CreateError):
        await usecase.execute(
            organization_id=10,
            email="user@example.com",
            role_uuid="role-uuid",
            team_uuid=None,
            actor_id=42,
        )


# ----------------------------- AcceptInvitationUseCase -----------------------------


@pytest.mark.asyncio
async def test_accept_invitation_usecase_success():
    from src.modules.workforce.application.usecases.invitation.accept_invitation_usecase import (
        AcceptInvitationUseCase,
    )

    invitation = _make_invitation(team_id=20)
    updated_invitation = _make_invitation(
        id=1, team_id=20, status=InvitationStatus.ACCEPTED
    )

    mock_invite_service = AsyncMock()
    mock_invite_service.ensure_acceptable = Mock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)
    mock_invite_service.mark_as_accepted = AsyncMock(return_value=updated_invitation)

    mock_membership_writer = AsyncMock()
    mock_membership = AsyncMock()
    mock_membership.id = 30
    mock_membership.uuid = "member-uuid"
    mock_membership_writer.create_membership = AsyncMock(return_value=mock_membership)

    mock_member_role_service = AsyncMock()
    mock_member_role_service.create_member_role = AsyncMock(
        return_value=_entity_without_events()
    )

    mock_team_member_service = AsyncMock()
    mock_team_member_service.add_team_member = AsyncMock(
        return_value=_entity_without_events()
    )

    usecase = AcceptInvitationUseCase(
        invitation_domain_service=mock_invite_service,
        organization_membership_writer=mock_membership_writer,
        rbac_member_role_domain_service=mock_member_role_service,
        team_member_domain_service=mock_team_member_service,
    )

    with patch(
        "src.modules.workforce.application.usecases.invitation.accept_invitation_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result_invite, result_membership = await usecase.execute(
            raw_token="raw_token",
            accepting_user_id=100,
            accepting_user_email="user@example.com",
        )

        assert result_invite is updated_invitation
        assert result_membership is mock_membership
        mock_invite_service.ensure_acceptable.assert_called_once()
        mock_membership_writer.create_membership.assert_awaited_once_with(
            organization_id=10, user_id=100, actor_id=100
        )
        mock_member_role_service.create_member_role.assert_awaited_once()
        mock_team_member_service.add_team_member.assert_awaited_once()
        mediator_mock.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_accept_invitation_usecase_without_team():
    from src.modules.workforce.application.usecases.invitation.accept_invitation_usecase import (
        AcceptInvitationUseCase,
    )

    invitation = _make_invitation(team_id=None)
    updated_invitation = _make_invitation(id=1, status=InvitationStatus.ACCEPTED)

    mock_invite_service = AsyncMock()
    mock_invite_service.ensure_acceptable = Mock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)
    mock_invite_service.mark_as_accepted = AsyncMock(return_value=updated_invitation)

    mock_membership_writer = AsyncMock()
    mock_membership = AsyncMock()
    mock_membership.id = 30
    mock_membership_writer.create_membership = AsyncMock(return_value=mock_membership)

    mock_member_role_service = AsyncMock()
    mock_member_role_service.create_member_role = AsyncMock(
        return_value=_entity_without_events()
    )

    usecase = AcceptInvitationUseCase(
        invitation_domain_service=mock_invite_service,
        organization_membership_writer=mock_membership_writer,
        rbac_member_role_domain_service=mock_member_role_service,
        team_member_domain_service=AsyncMock(),
    )

    with patch(
        "src.modules.workforce.application.usecases.invitation.accept_invitation_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        await usecase.execute(
            raw_token="raw_token",
            accepting_user_id=100,
            accepting_user_email="user@example.com",
        )

        mock_membership_writer.create_membership.assert_awaited_once()
        mediator_mock.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_accept_invitation_usecase_membership_fails():
    from src.modules.workforce.application.usecases.invitation.accept_invitation_usecase import (
        AcceptInvitationUseCase,
    )
    from src.shared.exceptions.base_exceptions import CreateError

    invitation = _make_invitation()

    mock_invite_service = AsyncMock()
    mock_invite_service.ensure_acceptable = Mock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)

    mock_membership_writer = AsyncMock()
    mock_membership = AsyncMock()
    mock_membership.id = None
    mock_membership_writer.create_membership = AsyncMock(return_value=mock_membership)

    usecase = AcceptInvitationUseCase(
        invitation_domain_service=mock_invite_service,
        organization_membership_writer=mock_membership_writer,
        rbac_member_role_domain_service=AsyncMock(),
        team_member_domain_service=AsyncMock(),
    )

    with pytest.raises(CreateError):
        await usecase.execute(
            raw_token="raw_token",
            accepting_user_id=100,
            accepting_user_email="user@example.com",
        )


# ----------------------------- GetInvitationByTokenUseCase -----------------------------


@pytest.mark.asyncio
async def test_get_invitation_by_token_usecase_success():
    from src.modules.workforce.application.usecases.invitation.get_invitation_by_token_usecase import (
        GetInvitationByTokenUseCase,
    )

    invitation = _make_invitation()
    organization = AsyncMock()
    organization.name = "Acme Org"
    role = _make_role()

    mock_invite_service = AsyncMock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)

    mock_org_reader = AsyncMock()
    mock_org_reader.get_organization = AsyncMock(return_value=organization)

    mock_role_service = AsyncMock()
    mock_role_service.get_role_by_id = AsyncMock(return_value=role)

    usecase = GetInvitationByTokenUseCase(
        invitation_domain_service=mock_invite_service,
        organization_reader=mock_org_reader,
        rbac_role_domain_service=mock_role_service,
    )

    result_invite, result_org, result_role = await usecase.execute("raw_token")

    assert result_invite is invitation
    assert result_org is not None
    assert result_org.name == "Acme Org"
    assert result_role is not None
    assert result_role.name == "Admin"


@pytest.mark.asyncio
async def test_get_invitation_by_token_usecase_revoked():
    from src.modules.workforce.application.usecases.invitation.get_invitation_by_token_usecase import (
        GetInvitationByTokenUseCase,
    )
    from src.shared.exceptions.base_exceptions import InvalidError

    invitation = _make_invitation(status=InvitationStatus.REVOKED)

    mock_invite_service = AsyncMock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)

    usecase = GetInvitationByTokenUseCase(
        invitation_domain_service=mock_invite_service,
        organization_reader=AsyncMock(),
        rbac_role_domain_service=AsyncMock(),
    )

    with pytest.raises(InvalidError):
        await usecase.execute("raw_token")


@pytest.mark.asyncio
async def test_get_invitation_by_token_usecase_accepted():
    from src.modules.workforce.application.usecases.invitation.get_invitation_by_token_usecase import (
        GetInvitationByTokenUseCase,
    )
    from src.shared.exceptions.base_exceptions import InvalidError

    invitation = _make_invitation(status=InvitationStatus.ACCEPTED)

    mock_invite_service = AsyncMock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)

    usecase = GetInvitationByTokenUseCase(
        invitation_domain_service=mock_invite_service,
        organization_reader=AsyncMock(),
        rbac_role_domain_service=AsyncMock(),
    )

    with pytest.raises(InvalidError):
        await usecase.execute("raw_token")


@pytest.mark.asyncio
async def test_get_invitation_by_token_usecase_expired():
    from src.modules.workforce.application.usecases.invitation.get_invitation_by_token_usecase import (
        GetInvitationByTokenUseCase,
    )
    from src.shared.exceptions.base_exceptions import InvalidError

    invitation = _make_invitation(
        status=InvitationStatus.PENDING,
        expires_at=datetime.now(UTC) - timedelta(hours=1),
    )

    mock_invite_service = AsyncMock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)

    usecase = GetInvitationByTokenUseCase(
        invitation_domain_service=mock_invite_service,
        organization_reader=AsyncMock(),
        rbac_role_domain_service=AsyncMock(),
    )

    with pytest.raises(InvalidError):
        await usecase.execute("raw_token")


# ----------------------------- ListInvitationsUseCase -----------------------------


@pytest.mark.asyncio
async def test_list_invitations_usecase_returns_invitations_and_users_map():
    from src.modules.workforce.application.usecases.invitation.list_invitations_usecase import (
        ListInvitationsUseCase,
    )

    invitations = [
        _make_invitation(id=1, invited_by_id=100),
        _make_invitation(id=2, invited_by_id=None),
    ]
    user = _make_user(id=100)

    mock_invite_service = AsyncMock()
    mock_invite_service.list_for_organization = AsyncMock(return_value=invitations)

    mock_user_reader = AsyncMock()
    mock_user_reader.get_users_by_ids = AsyncMock(return_value=[user])

    usecase = ListInvitationsUseCase(
        invitation_domain_service=mock_invite_service,
        user_reader=mock_user_reader,
    )

    result_invites, users_by_id = await usecase.execute()

    assert result_invites == invitations
    assert users_by_id == {100: user}
    mock_user_reader.get_users_by_ids.assert_awaited_once_with([100])


@pytest.mark.asyncio
async def test_list_invitations_usecase_reraises_domain_error():
    from src.modules.workforce.application.usecases.invitation.list_invitations_usecase import (
        ListInvitationsUseCase,
    )
    from src.shared.exceptions.base_exceptions import DomainError

    mock_invite_service = AsyncMock()
    mock_invite_service.list_for_organization = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    usecase = ListInvitationsUseCase(
        invitation_domain_service=mock_invite_service,
        user_reader=AsyncMock(),
    )

    with pytest.raises(DomainError):
        await usecase.execute()


# ----------------------------- RevokeInvitationUseCase -----------------------------


@pytest.mark.asyncio
async def test_revoke_invitation_usecase_publishes_events():
    from src.modules.workforce.application.usecases.invitation.revoke_invitation_usecase import (
        RevokeInvitationUseCase,
    )
    from src.modules.workforce.domain.events.invitation.invitation_domain_events import (
        InvitationRevokedEvent,
    )

    revoked = _make_invitation(status=InvitationStatus.REVOKED)
    revoked.add_event(InvitationRevokedEvent(invitation_id=1, organization_id=10))

    mock_invite_service = AsyncMock()
    mock_invite_service.revoke = AsyncMock(return_value=revoked)

    usecase = RevokeInvitationUseCase(invitation_domain_service=mock_invite_service)

    with patch(
        "src.modules.workforce.application.usecases.invitation.revoke_invitation_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result = await usecase.execute(invitation_uuid="uuid-abc")

        assert result is revoked
        mediator_mock.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_invitation_usecase_reraises_domain_error():
    from src.modules.workforce.application.usecases.invitation.revoke_invitation_usecase import (
        RevokeInvitationUseCase,
    )
    from src.shared.exceptions.base_exceptions import DomainError

    mock_invite_service = AsyncMock()
    mock_invite_service.revoke = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    usecase = RevokeInvitationUseCase(invitation_domain_service=mock_invite_service)

    with pytest.raises(DomainError):
        await usecase.execute(invitation_uuid="uuid-abc")


@pytest.mark.asyncio
async def test_revoke_invitation_usecase_wraps_unexpected_error():
    from src.modules.workforce.application.usecases.invitation.revoke_invitation_usecase import (
        RevokeInvitationUseCase,
    )
    from src.shared.exceptions.base_exceptions import UpdateError

    mock_invite_service = AsyncMock()
    mock_invite_service.revoke = AsyncMock(side_effect=ValueError("boom"))

    usecase = RevokeInvitationUseCase(invitation_domain_service=mock_invite_service)

    with pytest.raises(UpdateError):
        await usecase.execute(invitation_uuid="uuid-abc")


# ----------------------------- ResendInvitationUseCase -----------------------------


@pytest.mark.asyncio
async def test_resend_invitation_usecase_publishes_events():
    from src.modules.workforce.application.usecases.invitation.resend_invitation_usecase import (
        ResendInvitationUseCase,
    )
    from src.modules.workforce.domain.events.invitation.invitation_domain_events import (
        InvitationResentEvent,
    )

    new_invite = _make_invitation(id=99)
    new_invite.add_event(
        InvitationResentEvent(
            old_invitation_id=1,
            new_invitation_id=99,
            organization_id=10,
            email="user@example.com",
            raw_token="new_raw",
            expires_at=datetime.now(UTC) + INVITATION_TTL,
        )
    )

    mock_invite_service = AsyncMock()
    mock_invite_service.resend = AsyncMock(return_value=(new_invite, "new_raw"))

    usecase = ResendInvitationUseCase(invitation_domain_service=mock_invite_service)

    with patch(
        "src.modules.workforce.application.usecases.invitation.resend_invitation_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result_invite, result_token = await usecase.execute(
            invitation_uuid="uuid-abc", actor_id=42
        )

        assert result_invite.id == 99
        assert result_token == "new_raw"
        mediator_mock.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_resend_invitation_usecase_reraises_domain_error():
    from src.modules.workforce.application.usecases.invitation.resend_invitation_usecase import (
        ResendInvitationUseCase,
    )
    from src.shared.exceptions.base_exceptions import DomainError

    mock_invite_service = AsyncMock()
    mock_invite_service.resend = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    usecase = ResendInvitationUseCase(invitation_domain_service=mock_invite_service)

    with pytest.raises(DomainError):
        await usecase.execute(invitation_uuid="uuid-abc", actor_id=42)


# ----------------------------- SignupAndAcceptInvitationUseCase -----------------------------


@pytest.mark.asyncio
async def test_signup_and_accept_usecase_success():
    from src.modules.workforce.application.usecases.invitation.signup_and_accept_invitation_usecase import (
        SignupAndAcceptInvitationUseCase,
    )

    invitation = _make_invitation(team_id=20)
    updated_invitation = _make_invitation(
        id=1, status=InvitationStatus.ACCEPTED, team_id=20
    )

    mock_invite_service = AsyncMock()
    mock_invite_service.ensure_acceptable = Mock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)
    mock_invite_service.mark_as_accepted = AsyncMock(return_value=updated_invitation)

    mock_user_provisioner = AsyncMock()
    provisioned = AsyncMock()
    provisioned.user_id = 200
    provisioned.user_uuid = "user-uuid"
    provisioned.email = "user@example.com"
    provisioned.session_uuid = "session-uuid"
    mock_user_provisioner.provision_invited_user = AsyncMock(return_value=provisioned)

    mock_membership_writer = AsyncMock()
    mock_membership = AsyncMock()
    mock_membership.id = 30
    mock_membership.uuid = "member-uuid"
    mock_membership_writer.create_membership = AsyncMock(return_value=mock_membership)

    mock_member_role_service = AsyncMock()
    mock_member_role_service.create_member_role = AsyncMock(
        return_value=_entity_without_events()
    )
    mock_team_member_service = AsyncMock()
    mock_team_member_service.add_team_member = AsyncMock(
        return_value=_entity_without_events()
    )

    usecase = SignupAndAcceptInvitationUseCase(
        invitation_domain_service=mock_invite_service,
        user_provisioner=mock_user_provisioner,
        organization_membership_writer=mock_membership_writer,
        rbac_member_role_domain_service=mock_member_role_service,
        team_member_domain_service=mock_team_member_service,
    )

    with patch(
        "src.modules.workforce.application.usecases.invitation.signup_and_accept_invitation_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result_invite, result_membership, result_provisioned = await usecase.execute(
            raw_token="raw_token",
            password="Secure123!",
            full_name="Test User",
        )

        assert result_invite is updated_invitation
        assert result_membership is mock_membership
        assert result_provisioned is provisioned
        mock_invite_service.ensure_acceptable.assert_called_once()
        mock_user_provisioner.provision_invited_user.assert_awaited_once_with(
            email="user@example.com",
            password="Secure123!",
            full_name="Test User",
        )
        mock_membership_writer.create_membership.assert_awaited_once_with(
            organization_id=10, user_id=200, actor_id=200
        )
        mediator_mock.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_signup_and_accept_usecase_without_team():
    from src.modules.workforce.application.usecases.invitation.signup_and_accept_invitation_usecase import (
        SignupAndAcceptInvitationUseCase,
    )

    invitation = _make_invitation(team_id=None)
    updated_invitation = _make_invitation(id=1, status=InvitationStatus.ACCEPTED)

    mock_invite_service = AsyncMock()
    mock_invite_service.ensure_acceptable = Mock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)
    mock_invite_service.mark_as_accepted = AsyncMock(return_value=updated_invitation)

    mock_user_provisioner = AsyncMock()
    provisioned = AsyncMock()
    provisioned.user_id = 200
    mock_user_provisioner.provision_invited_user = AsyncMock(return_value=provisioned)

    mock_membership_writer = AsyncMock()
    mock_membership = AsyncMock()
    mock_membership.id = 30
    mock_membership_writer.create_membership = AsyncMock(return_value=mock_membership)

    mock_member_role_service = AsyncMock()
    mock_member_role_service.create_member_role = AsyncMock(
        return_value=_entity_without_events()
    )

    usecase = SignupAndAcceptInvitationUseCase(
        invitation_domain_service=mock_invite_service,
        user_provisioner=mock_user_provisioner,
        organization_membership_writer=mock_membership_writer,
        rbac_member_role_domain_service=mock_member_role_service,
        team_member_domain_service=AsyncMock(),
    )

    with patch(
        "src.modules.workforce.application.usecases.invitation.signup_and_accept_invitation_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        await usecase.execute(
            raw_token="raw_token",
            password="Secure123!",
            full_name=None,
        )

        mock_membership_writer.create_membership.assert_awaited_once()
        mediator_mock.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_signup_and_accept_usecase_existing_user_raises_conflict():
    from src.modules.workforce.application.usecases.invitation.signup_and_accept_invitation_usecase import (
        SignupAndAcceptInvitationUseCase,
    )
    from src.shared.exceptions.base_exceptions import ConflictError

    invitation = _make_invitation()

    mock_invite_service = AsyncMock()
    mock_invite_service.ensure_acceptable = Mock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)

    mock_user_provisioner = AsyncMock()
    mock_user_provisioner.provision_invited_user = AsyncMock(
        side_effect=ConflictError(error="duplicate email")
    )

    usecase = SignupAndAcceptInvitationUseCase(
        invitation_domain_service=mock_invite_service,
        user_provisioner=mock_user_provisioner,
        organization_membership_writer=AsyncMock(),
        rbac_member_role_domain_service=AsyncMock(),
        team_member_domain_service=AsyncMock(),
    )

    with pytest.raises(ConflictError) as exc_info:
        await usecase.execute(
            raw_token="raw_token",
            password="Secure123!",
            full_name=None,
        )

    assert "account already exists" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_signup_and_accept_usecase_membership_fails():
    from src.modules.workforce.application.usecases.invitation.signup_and_accept_invitation_usecase import (
        SignupAndAcceptInvitationUseCase,
    )
    from src.shared.exceptions.base_exceptions import ServerError

    invitation = _make_invitation()

    mock_invite_service = AsyncMock()
    mock_invite_service.ensure_acceptable = Mock()
    mock_invite_service.get_by_raw_token = AsyncMock(return_value=invitation)

    mock_user_provisioner = AsyncMock()
    provisioned = AsyncMock()
    provisioned.user_id = 200
    mock_user_provisioner.provision_invited_user = AsyncMock(return_value=provisioned)

    mock_membership_writer = AsyncMock()
    mock_membership = AsyncMock()
    mock_membership.id = None
    mock_membership_writer.create_membership = AsyncMock(return_value=mock_membership)

    usecase = SignupAndAcceptInvitationUseCase(
        invitation_domain_service=mock_invite_service,
        user_provisioner=mock_user_provisioner,
        organization_membership_writer=mock_membership_writer,
        rbac_member_role_domain_service=AsyncMock(),
        team_member_domain_service=AsyncMock(),
    )

    with pytest.raises(ServerError):
        await usecase.execute(
            raw_token="raw_token",
            password="Secure123!",
            full_name=None,
        )
