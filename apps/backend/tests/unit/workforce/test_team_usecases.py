from unittest.mock import AsyncMock, patch

import pytest


# ----------------------------- Factories -----------------------------


def _make_team(**overrides):
    from src.modules.workforce.domain.entities.team.team_entity import TeamEntity

    data = {
        "id": 1,
        "name": "Engineering",
        "description": "desc",
        "color": None,
        "timezone": None,
        "is_default": False,
        "organization_id": 10,
        "created_by_id": 42,
    }
    data.update(overrides)
    return TeamEntity(**data)


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


def _make_user(**overrides):
    from src.modules.auth.domain.entities.user_entity import UserEntity

    data = {
        "id": 100,
        "username": "testuser",
        "email": "user@example.com",
        "avatar_bg": "#abcdef",
        "status": "active",
        "is_onboarded": True,
        "full_name": "Test User",
    }
    data.update(overrides)
    return UserEntity(**data)


def _make_org_member(**overrides):
    from src.modules.organization.domain.entities.organization_member_entity import (
        OrganizationMemberEntity,
    )

    data = {
        "id": 20,
        "organization_id": 10,
        "user_id": 100,
        "status": "active",
    }
    data.update(overrides)
    return OrganizationMemberEntity(**data)


def _make_org_member_reader(members=None):
    """
    Build a mock OrganizationMemberReader. Defaults to a single active member
    (id=20, organization_id=10) so the cross-org guard in the team use cases
    passes for the standard member_id=20 used throughout these tests.
    """
    reader = AsyncMock()
    reader.get_members_by_ids = AsyncMock(
        return_value=members if members is not None else [_make_org_member()]
    )
    return reader


def _make_member_role_reader(role=None, member_id=20):
    """
    Build a mock MemberRoleReader resolving `member_id` to `role` (None == no
    assigned role). Used to exercise the owner-protection rule on the default
    team in RemoveTeamMemberUseCase.
    """
    reader = AsyncMock()
    reader.get_member_roles = AsyncMock(return_value={member_id: role})
    return reader


# ----------------------------- CreateTeamUseCase -----------------------------


def _make_create_team_usecase(
    *,
    team_service,
    member_service=None,
    org_member_reader=None,
    organization_id=10,
):
    from src.modules.workforce.application.usecases.team.create_team_usecase import (
        CreateTeamUseCase,
    )

    if member_service is None:
        member_service = AsyncMock()
        member_service.add_team_member = AsyncMock(
            return_value=_make_team_member(id=77)
        )
    if org_member_reader is None:
        org_member_reader = AsyncMock()
        org_member_reader.get_member_by_user_id = AsyncMock(
            return_value=_make_org_member(id=20)
        )

    return CreateTeamUseCase(
        team_domain_service=team_service,
        team_member_domain_service=member_service,
        organization_member_reader=org_member_reader,
        organization_id=organization_id,
    )


@pytest.mark.asyncio
async def test_create_team_usecase_adds_creator_as_lead_and_publishes_events():
    from src.modules.workforce.domain.events.team.team_domain_events import (
        TeamCreatedEvent,
        TeamMemberAddedEvent,
    )

    created = _make_team(id=99)
    created.add_event(
        TeamCreatedEvent(team_id=99, organization_id=10, name="Engineering")
    )

    mock_service = AsyncMock()
    mock_service.create_team = AsyncMock(return_value=created)

    # The creator's user id (42) resolves to org membership id 20.
    org_member_reader = AsyncMock()
    org_member_reader.get_member_by_user_id = AsyncMock(
        return_value=_make_org_member(id=20)
    )

    lead_member = _make_team_member(id=77, team_id=99, member_id=20, role="team_lead")
    lead_member.add_event(
        TeamMemberAddedEvent(
            team_member_id=77,
            organization_id=10,
            team_id=99,
            member_id=20,
            role="team_lead",
        )
    )
    member_service = AsyncMock()
    member_service.add_team_member = AsyncMock(return_value=lead_member)

    usecase = _make_create_team_usecase(
        team_service=mock_service,
        member_service=member_service,
        org_member_reader=org_member_reader,
    )

    with patch(
        "src.modules.workforce.application.usecases.team.create_team_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result = await usecase.execute(
            organization_id=10,
            name="Engineering",
            description="desc",
            color=None,
            timezone=None,
            is_default=False,
            actor_id=42,
        )

        assert result.id == 99

        # Creator (org member 20) is added as a team lead of the new team.
        org_member_reader.get_member_by_user_id.assert_awaited_once_with(10, 42)
        member_service.add_team_member.assert_awaited_once()
        added_entity = member_service.add_team_member.await_args.args[0]
        assert added_entity.team_id == 99
        assert added_entity.member_id == 20
        assert added_entity.role == "team_lead"
        assert added_entity.created_by_id == 42

        # Both the team-created and member-added events are published.
        published = [c.args[0] for c in mediator_mock.publish.await_args_list]
        assert any(isinstance(e, TeamCreatedEvent) for e in published)
        assert any(isinstance(e, TeamMemberAddedEvent) for e in published)


@pytest.mark.asyncio
async def test_create_team_usecase_actor_not_member_raises_create_error():
    from src.shared.exceptions.base_exceptions import CreateError

    created = _make_team(id=99)
    mock_service = AsyncMock()
    mock_service.create_team = AsyncMock(return_value=created)

    org_member_reader = AsyncMock()
    org_member_reader.get_member_by_user_id = AsyncMock(return_value=None)

    member_service = AsyncMock()

    usecase = _make_create_team_usecase(
        team_service=mock_service,
        member_service=member_service,
        org_member_reader=org_member_reader,
    )

    with pytest.raises(CreateError):
        await usecase.execute(
            organization_id=10,
            name="Engineering",
            description="desc",
            color=None,
            timezone=None,
            is_default=False,
            actor_id=42,
        )

    member_service.add_team_member.assert_not_called()


@pytest.mark.asyncio
async def test_create_team_usecase_returns_invalid_entity_raises_create_error():
    from src.shared.exceptions.base_exceptions import CreateError

    mock_service = AsyncMock()
    mock_service.create_team = AsyncMock(return_value=_make_team(id=None))

    usecase = _make_create_team_usecase(team_service=mock_service)

    with pytest.raises(CreateError):
        await usecase.execute(
            organization_id=10,
            name="Engineering",
            description="desc",
            color=None,
            timezone=None,
            is_default=False,
            actor_id=42,
        )


@pytest.mark.asyncio
async def test_create_team_usecase_reraises_domain_error():
    from src.shared.exceptions.base_exceptions import DomainError

    mock_service = AsyncMock()
    mock_service.create_team = AsyncMock(side_effect=DomainError(error="dup"))

    usecase = _make_create_team_usecase(team_service=mock_service)

    with pytest.raises(DomainError):
        await usecase.execute(
            organization_id=10,
            name="Engineering",
            description="desc",
            color=None,
            timezone=None,
            is_default=False,
            actor_id=42,
        )


# ----------------------------- ListTeamsUseCase -----------------------------


@pytest.mark.asyncio
async def test_list_teams_usecase_returns_teams_total_users_leads_and_members():
    from src.modules.workforce.application.usecases.team.list_teams_usecase import (
        ListTeamsUseCase,
    )

    teams = [_make_team(id=1, created_by_id=100), _make_team(id=2, created_by_id=None)]
    creator = _make_user(id=100, email="creator@x.com")
    lead_user = _make_user(id=200, email="lead@x.com")
    member_user = _make_user(id=201, email="member@x.com")

    # Team 1 has a lead (member 20 -> user 200) and a regular member
    # (member 21 -> user 201). Repo returns members ordered by id ascending.
    lead_member = _make_team_member(id=5, team_id=1, member_id=20, role="team_lead")
    regular_member = _make_team_member(id=6, team_id=1, member_id=21, role="member")
    org_members = [
        _make_org_member(id=20, user_id=200),
        _make_org_member(id=21, user_id=201),
    ]

    mock_service = AsyncMock()
    mock_service.list_teams_by_organization_id = AsyncMock(return_value=(teams, 2))

    mock_member_service = AsyncMock()
    mock_member_service.list_members_by_team_ids = AsyncMock(
        return_value=[lead_member, regular_member]
    )

    org_member_reader = AsyncMock()
    org_member_reader.get_members_by_ids = AsyncMock(return_value=org_members)

    user_reader = AsyncMock()
    user_reader.get_users_by_ids = AsyncMock(
        return_value=[creator, lead_user, member_user]
    )

    usecase = ListTeamsUseCase(
        team_domain_service=mock_service,
        team_member_domain_service=mock_member_service,
        organization_member_reader=org_member_reader,
        user_reader=user_reader,
    )
    (
        teams_out,
        total,
        users_map,
        lead_user_by_team_id,
        members_by_team_id,
    ) = await usecase.execute(status="active", limit=20, offset=0)

    assert teams_out == teams
    assert total == 2
    assert users_map == {100: creator, 200: lead_user, 201: member_user}
    assert lead_user_by_team_id == {1: lead_user}

    # Team 1 carries both members, each paired with the resolved user.
    assert members_by_team_id == {
        1: [(lead_member, lead_user), (regular_member, member_user)]
    }

    mock_service.list_teams_by_organization_id.assert_awaited_once_with(
        status="active", limit=20, offset=0
    )
    mock_member_service.list_members_by_team_ids.assert_awaited_once_with([1, 2])
    assert set(org_member_reader.get_members_by_ids.await_args.args[0]) == {20, 21}
    # Creator and all member user ids are resolved in a single batch.
    called_with = set(user_reader.get_users_by_ids.await_args.args[0])
    assert called_with == {100, 200, 201}


@pytest.mark.asyncio
async def test_list_teams_usecase_no_members_yields_empty_maps():
    from src.modules.workforce.application.usecases.team.list_teams_usecase import (
        ListTeamsUseCase,
    )

    teams = [_make_team(id=1, created_by_id=100)]
    creator = _make_user(id=100)

    mock_service = AsyncMock()
    mock_service.list_teams_by_organization_id = AsyncMock(return_value=(teams, 1))

    mock_member_service = AsyncMock()
    mock_member_service.list_members_by_team_ids = AsyncMock(return_value=[])

    org_member_reader = AsyncMock()
    org_member_reader.get_members_by_ids = AsyncMock(return_value=[])

    user_reader = AsyncMock()
    user_reader.get_users_by_ids = AsyncMock(return_value=[creator])

    usecase = ListTeamsUseCase(
        team_domain_service=mock_service,
        team_member_domain_service=mock_member_service,
        organization_member_reader=org_member_reader,
        user_reader=user_reader,
    )
    (
        teams_out,
        total,
        users_map,
        lead_user_by_team_id,
        members_by_team_id,
    ) = await usecase.execute()

    assert teams_out == teams
    assert total == 1
    assert users_map == {100: creator}
    assert lead_user_by_team_id == {}
    assert members_by_team_id == {}
    mock_service.list_teams_by_organization_id.assert_awaited_once_with(
        status=None, limit=50, offset=0
    )
    mock_member_service.list_members_by_team_ids.assert_awaited_once_with([1])


@pytest.mark.asyncio
async def test_list_teams_usecase_picks_first_lead_when_multiple():
    from src.modules.workforce.application.usecases.team.list_teams_usecase import (
        ListTeamsUseCase,
    )

    teams = [_make_team(id=1, created_by_id=None)]

    # Two leads on the same team. The repo returns members ordered by id
    # ascending, so the first lead encountered (lowest id) wins.
    lead_low = _make_team_member(id=3, team_id=1, member_id=22, role="team_lead")
    lead_high = _make_team_member(id=9, team_id=1, member_id=21, role="team_lead")
    org_members = [
        _make_org_member(id=21, user_id=210),
        _make_org_member(id=22, user_id=220),
    ]
    user_a = _make_user(id=210, email="a@x.com")
    user_b = _make_user(id=220, email="b@x.com")

    mock_service = AsyncMock()
    mock_service.list_teams_by_organization_id = AsyncMock(return_value=(teams, 1))

    mock_member_service = AsyncMock()
    mock_member_service.list_members_by_team_ids = AsyncMock(
        return_value=[lead_low, lead_high]
    )

    org_member_reader = AsyncMock()
    org_member_reader.get_members_by_ids = AsyncMock(return_value=org_members)

    user_reader = AsyncMock()
    user_reader.get_users_by_ids = AsyncMock(return_value=[user_a, user_b])

    usecase = ListTeamsUseCase(
        team_domain_service=mock_service,
        team_member_domain_service=mock_member_service,
        organization_member_reader=org_member_reader,
        user_reader=user_reader,
    )
    _, _, _, lead_user_by_team_id, _ = await usecase.execute()

    # lead_low has the lower membership id (3 < 9) -> its user (220) wins.
    assert lead_user_by_team_id == {1: user_b}


# ----------------------------- GetTeamUseCase -----------------------------


@pytest.mark.asyncio
async def test_get_team_usecase_resolves_creator():
    from src.modules.workforce.application.usecases.team.get_team_usecase import (
        GetTeamUseCase,
    )

    team = _make_team(created_by_id=100)
    user = _make_user(id=100)

    mock_service = AsyncMock()
    mock_service.get_team_by_uuid = AsyncMock(return_value=team)

    user_reader = AsyncMock()
    user_reader.get_user = AsyncMock(return_value=user)

    usecase = GetTeamUseCase(team_domain_service=mock_service, user_reader=user_reader)
    returned_team, created_by = await usecase.execute("abc")

    assert returned_team is team
    assert created_by is user
    user_reader.get_user.assert_awaited_once_with(100)


@pytest.mark.asyncio
async def test_get_team_usecase_no_creator_skips_user_lookup():
    from src.modules.workforce.application.usecases.team.get_team_usecase import (
        GetTeamUseCase,
    )

    team = _make_team(created_by_id=None)

    mock_service = AsyncMock()
    mock_service.get_team_by_uuid = AsyncMock(return_value=team)
    user_reader = AsyncMock()

    usecase = GetTeamUseCase(team_domain_service=mock_service, user_reader=user_reader)
    returned_team, created_by = await usecase.execute("abc")

    assert returned_team is team
    assert created_by is None
    user_reader.get_user.assert_not_called()


# ----------------------------- UpdateTeamUseCase -----------------------------


@pytest.mark.asyncio
async def test_update_team_usecase_publishes_events():
    from src.modules.workforce.application.usecases.team.update_team_usecase import (
        UpdateTeamUseCase,
    )
    from src.modules.workforce.domain.events.team.team_domain_events import (
        TeamUpdatedEvent,
    )

    updated = _make_team()
    updated.add_event(TeamUpdatedEvent(team_id=1, organization_id=10))

    mock_service = AsyncMock()
    mock_service.update_team = AsyncMock(return_value=updated)

    usecase = UpdateTeamUseCase(team_domain_service=mock_service)

    with patch(
        "src.modules.workforce.application.usecases.team.update_team_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result = await usecase.execute(team_uuid="abc", actor_id=42, name="Renamed")

        assert result is updated
        mediator_mock.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_team_usecase_reraises_domain_error():
    from src.modules.workforce.application.usecases.team.update_team_usecase import (
        UpdateTeamUseCase,
    )
    from src.shared.exceptions.base_exceptions import DomainError

    mock_service = AsyncMock()
    mock_service.update_team = AsyncMock(side_effect=DomainError(error="x"))

    usecase = UpdateTeamUseCase(team_domain_service=mock_service)

    with pytest.raises(DomainError):
        await usecase.execute(team_uuid="abc", actor_id=42, name="Renamed")


# ----------------------------- DeleteTeamUseCase -----------------------------


@pytest.mark.asyncio
async def test_delete_team_usecase_clears_members_and_publishes_events():
    from src.modules.workforce.application.usecases.team.delete_team_usecase import (
        DeleteTeamUseCase,
    )
    from src.modules.workforce.domain.events.team.team_domain_events import (
        TeamDeletedEvent,
    )

    deleted = _make_team()
    deleted.add_event(TeamDeletedEvent(team_id=1, organization_id=10))

    mock_team_service = AsyncMock()
    mock_team_service.delete_team = AsyncMock(return_value=deleted)

    mock_member_service = AsyncMock()
    mock_member_service.remove_all_members = AsyncMock()

    usecase = DeleteTeamUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=mock_member_service,
    )

    with patch(
        "src.modules.workforce.application.usecases.team.delete_team_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        await usecase.execute(team_uuid="abc")

        mock_member_service.remove_all_members.assert_awaited_once_with(1)
        mediator_mock.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_team_usecase_reraises_domain_error():
    from src.modules.workforce.application.usecases.team.delete_team_usecase import (
        DeleteTeamUseCase,
    )
    from src.shared.exceptions.base_exceptions import DomainError

    mock_team_service = AsyncMock()
    mock_team_service.delete_team = AsyncMock(side_effect=DomainError(error="x"))

    usecase = DeleteTeamUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=AsyncMock(),
    )

    with pytest.raises(DomainError):
        await usecase.execute(team_uuid="abc")


# ----------------------------- AddTeamMembersUseCase -----------------------------


def _make_bulk_usecase(
    *,
    team_service,
    member_service,
    users,
    org_members,
    organization_id=10,
):
    """
    Wire an AddTeamMembersUseCase with mock readers. `users` and `org_members`
    seed the uuid->user->org-member resolution chain.
    """
    from src.modules.workforce.application.usecases.team.add_team_members_usecase import (
        AddTeamMembersUseCase,
    )

    user_reader = AsyncMock()
    user_reader.get_users_by_uuids = AsyncMock(return_value=users)

    org_member_reader = AsyncMock()
    org_member_reader.get_members_by_user_ids = AsyncMock(return_value=org_members)

    return AddTeamMembersUseCase(
        team_domain_service=team_service,
        team_member_domain_service=member_service,
        organization_member_reader=org_member_reader,
        user_reader=user_reader,
        organization_id=organization_id,
    )


def _adding_member_service(existing=None):
    """
    A team_member_domain_service mock whose add/update return the entity they
    were given, stamped with an id and carrying the matching domain event so the
    use case can publish it.
    """
    from src.modules.workforce.domain.events.team.team_domain_events import (
        TeamMemberAddedEvent,
        TeamMemberRoleAssignedEvent,
    )

    service = AsyncMock()
    service.list_team_members = AsyncMock(return_value=existing or [])

    async def fake_add(entity, *, organization_id):
        entity.id = 1000 + entity.member_id
        entity.add_event(
            TeamMemberAddedEvent(
                team_member_id=entity.id,
                organization_id=organization_id,
                team_id=entity.team_id,
                member_id=entity.member_id,
                role=entity.role,
            )
        )
        return entity

    async def fake_set_role(
        *, team_id, member_id, role, organization_id, actor_id=None
    ):
        entity = _make_team_member(
            id=2000 + member_id, team_id=team_id, member_id=member_id, role=role
        )
        assert entity.id is not None
        team_member_id: int = entity.id
        entity.add_event(
            TeamMemberRoleAssignedEvent(
                team_member_id=team_member_id,
                organization_id=organization_id,
                team_id=team_id,
                member_id=member_id,
                role=role,
            )
        )
        return entity

    service.add_team_member = AsyncMock(side_effect=fake_add)
    service.set_member_role = AsyncMock(side_effect=fake_set_role)
    return service


@pytest.mark.asyncio
async def test_add_team_members_adds_new_members_with_roles():
    team = _make_team(id=10)
    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    member_service = _adding_member_service(existing=[])

    users = [
        _make_user(id=200, uuid="ua"),
        _make_user(id=201, uuid="ub"),
        _make_user(id=202, uuid="uc"),
    ]
    org_members = [
        _make_org_member(id=20, user_id=200),
        _make_org_member(id=21, user_id=201),
        _make_org_member(id=22, user_id=202),
    ]

    usecase = _make_bulk_usecase(
        team_service=mock_team_service,
        member_service=member_service,
        users=users,
        org_members=org_members,
    )

    with patch(
        "src.modules.workforce.application.usecases.team.add_team_members_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result = await usecase.execute(
            team_uuid="abc",
            members=["ua"],
            supervisors=["ub"],
            lead="uc",
            actor_id=7,
        )

    assert member_service.add_team_member.await_count == 3
    role_by_member = {m.member_id: m.role for m in result}
    assert role_by_member == {20: "member", 21: "supervisor", 22: "team_lead"}
    assert mediator_mock.publish.await_count == 3


@pytest.mark.asyncio
async def test_add_team_members_enforces_single_lead():
    team = _make_team(id=10)
    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    # An existing lead (member 30) that must be demoted when a new lead arrives.
    current_lead = _make_team_member(id=5, team_id=10, member_id=30, role="team_lead")
    member_service = _adding_member_service(existing=[current_lead])

    users = [_make_user(id=202, uuid="uc")]
    org_members = [_make_org_member(id=22, user_id=202)]

    usecase = _make_bulk_usecase(
        team_service=mock_team_service,
        member_service=member_service,
        users=users,
        org_members=org_members,
    )

    with patch(
        "src.modules.workforce.application.usecases.team.add_team_members_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        await usecase.execute(
            team_uuid="abc",
            members=[],
            supervisors=[],
            lead="uc",
            actor_id=7,
        )

    # The previous lead (member 30) is demoted to member.
    demote_calls = [
        c
        for c in member_service.set_member_role.await_args_list
        if c.kwargs.get("member_id") == 30
    ]
    assert len(demote_calls) == 1
    assert demote_calls[0].kwargs["role"] == "member"
    # The new lead (member 22) is added with the team_lead role.
    member_service.add_team_member.assert_awaited_once()
    added = member_service.add_team_member.await_args.args[0]
    assert added.member_id == 22
    assert added.role == "team_lead"


@pytest.mark.asyncio
async def test_add_team_members_existing_member_rejected_with_bucketed_error():
    from src.shared.exceptions.base_exceptions import InvalidError

    team = _make_team(id=10)
    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    # Member 20 is already on the team; re-adding them under any bucket fails.
    existing_member = _make_team_member(id=5, team_id=10, member_id=20, role="member")
    member_service = _adding_member_service(existing=[existing_member])

    users = [_make_user(id=200, uuid="ua", email="dup@example.com")]
    org_members = [_make_org_member(id=20, user_id=200)]

    usecase = _make_bulk_usecase(
        team_service=mock_team_service,
        member_service=member_service,
        users=users,
        org_members=org_members,
    )

    with pytest.raises(InvalidError) as exc_info:
        await usecase.execute(
            team_uuid="abc",
            members=[],
            supervisors=["ua"],
            lead=None,
            actor_id=7,
        )

    # The offending email is reported under the bucket it was sent in, and
    # nothing is written (all-or-nothing -> the UOW rolls back).
    assert exc_info.value.errors == {
        "supervisor": "dup@example.com is already on the team"
    }
    member_service.add_team_member.assert_not_called()
    member_service.set_member_role.assert_not_called()


@pytest.mark.asyncio
async def test_add_team_members_unknown_uuid_is_all_or_nothing():
    from src.shared.exceptions.base_exceptions import InvalidError

    team = _make_team(id=10)
    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    member_service = _adding_member_service(existing=[])

    # Only one of the two requested uuids resolves to a user.
    users = [_make_user(id=200, uuid="ua")]
    org_members = [_make_org_member(id=20, user_id=200)]

    usecase = _make_bulk_usecase(
        team_service=mock_team_service,
        member_service=member_service,
        users=users,
        org_members=org_members,
    )

    with pytest.raises(InvalidError) as exc_info:
        await usecase.execute(
            team_uuid="abc",
            members=["ua", "missing"],
            supervisors=[],
            lead=None,
            actor_id=7,
        )

    # The unresolved uuid is reported under the bucket it was sent in.
    assert exc_info.value.errors == {"member": "user email not found"}
    member_service.add_team_member.assert_not_called()
    member_service.set_member_role.assert_not_called()


@pytest.mark.asyncio
async def test_add_team_members_duplicate_role_assignment_rejected():
    from src.shared.exceptions.base_exceptions import InvalidError

    usecase = _make_bulk_usecase(
        team_service=AsyncMock(),
        member_service=_adding_member_service(existing=[]),
        users=[],
        org_members=[],
    )

    with pytest.raises(InvalidError):
        await usecase.execute(
            team_uuid="abc",
            members=["ua"],
            supervisors=["ua"],
            lead=None,
            actor_id=7,
        )


@pytest.mark.asyncio
async def test_add_team_members_non_org_member_rejected():
    from src.shared.exceptions.base_exceptions import InvalidError

    team = _make_team(id=10)
    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    member_service = _adding_member_service(existing=[])

    # User resolves, but has no active membership in this organization.
    users = [_make_user(id=200, uuid="ua")]
    org_members = []

    usecase = _make_bulk_usecase(
        team_service=mock_team_service,
        member_service=member_service,
        users=users,
        org_members=org_members,
    )

    with pytest.raises(InvalidError):
        await usecase.execute(
            team_uuid="abc",
            members=["ua"],
            supervisors=[],
            lead=None,
            actor_id=7,
        )

    member_service.add_team_member.assert_not_called()


@pytest.mark.asyncio
async def test_add_team_members_team_without_id_raises_create_error():
    from src.shared.exceptions.base_exceptions import CreateError

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=_make_team(id=None))

    usecase = _make_bulk_usecase(
        team_service=mock_team_service,
        member_service=_adding_member_service(existing=[]),
        users=[_make_user(id=200, uuid="ua")],
        org_members=[_make_org_member(id=20, user_id=200)],
    )

    with pytest.raises(CreateError):
        await usecase.execute(
            team_uuid="abc",
            members=["ua"],
            supervisors=[],
            lead=None,
            actor_id=7,
        )


# ----------------------------- ListTeamMembersUseCase -----------------------------


@pytest.mark.asyncio
async def test_list_team_members_usecase_resolves_member_and_added_by_users():
    from src.modules.workforce.application.usecases.team.list_team_members_usecase import (
        ListTeamMembersUseCase,
    )

    team = _make_team(id=10)
    members = [
        _make_team_member(id=1, member_id=20, created_by_id=100),
        _make_team_member(id=2, member_id=21, created_by_id=None),
    ]
    org_members = [
        _make_org_member(id=20, user_id=200),
        _make_org_member(id=21, user_id=201),
    ]
    users = [
        _make_user(id=100, email="adder@x.com"),
        _make_user(id=200, email="alice@x.com"),
        _make_user(id=201, email="bob@x.com"),
    ]

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    mock_member_service = AsyncMock()
    mock_member_service.list_team_members = AsyncMock(return_value=members)
    mock_member_service.list_members_paginated = AsyncMock(
        return_value=(members, None, None, False, False)
    )

    mock_org_member_reader = AsyncMock()
    mock_org_member_reader.get_members_by_ids = AsyncMock(return_value=org_members)

    mock_user_reader = AsyncMock()
    mock_user_reader.get_users_by_ids = AsyncMock(return_value=users)

    usecase = ListTeamMembersUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=mock_member_service,
        organization_member_reader=mock_org_member_reader,
        user_reader=mock_user_reader,
    )

    (
        returned_team,
        returned_members,
        total_member_count,
        member_user_by_member_id,
        users_by_id,
        _prev_cursor,
        _next_cursor,
        _has_previous_page,
        _has_next_page,
    ) = await usecase.execute(team_uuid="abc", organization_id=10)

    assert returned_team is team
    assert returned_members == members
    # member_id -> resolved user
    member_20 = member_user_by_member_id[20]
    member_21 = member_user_by_member_id[21]
    assert member_20 is not None and member_20.id == 200
    assert member_21 is not None and member_21.id == 201
    # users_by_id includes both member-users and added_by users
    assert set(users_by_id.keys()) == {100, 200, 201}

    mock_org_member_reader.get_members_by_ids.assert_awaited_once_with([20, 21])
    # User reader is called with the union of member-user-ids and added-by-ids
    user_reader_call = mock_user_reader.get_users_by_ids.await_args
    assert user_reader_call is not None
    called_with = set(user_reader_call.args[0])
    assert called_with == {100, 200, 201}


@pytest.mark.asyncio
async def test_list_team_members_usecase_team_without_id_raises_server_error():
    from src.modules.workforce.application.usecases.team.list_team_members_usecase import (
        ListTeamMembersUseCase,
    )
    from src.shared.exceptions.base_exceptions import ServerError

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=_make_team(id=None))

    usecase = ListTeamMembersUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=AsyncMock(),
        organization_member_reader=AsyncMock(),
        user_reader=AsyncMock(),
    )

    with pytest.raises(ServerError):
        await usecase.execute(team_uuid="abc", organization_id=10)


# ----------------------------- RemoveTeamMemberUseCase -----------------------------


@pytest.mark.asyncio
async def test_remove_team_member_usecase_success():
    from src.modules.workforce.application.usecases.team.remove_team_member_usecase import (
        RemoveTeamMemberUseCase,
    )

    team = _make_team(id=10)

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    removed_member = _make_team_member(id=1, member_id=20)

    mock_member_service = AsyncMock()
    mock_member_service.remove_team_member = AsyncMock(return_value=removed_member)

    usecase = RemoveTeamMemberUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=mock_member_service,
        organization_member_reader=_make_org_member_reader(),
        member_role_reader=_make_member_role_reader(),
        organization_id=10,
    )
    await usecase.execute(team_uuid="abc", member_id=20)

    mock_member_service.remove_team_member.assert_awaited_once_with(
        team_id=10, member_id=20, organization_id=10
    )


@pytest.mark.asyncio
async def test_remove_team_member_usecase_owner_blocked_on_default_team():
    from src.modules.workforce.application.usecases.team.remove_team_member_usecase import (
        RemoveTeamMemberUseCase,
    )
    from src.shared.exceptions.base_exceptions import ConflictError

    team = _make_team(id=10, is_default=True)

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    mock_member_service = AsyncMock()

    usecase = RemoveTeamMemberUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=mock_member_service,
        organization_member_reader=_make_org_member_reader(),
        member_role_reader=_make_member_role_reader(role="owner"),
        organization_id=10,
    )

    with pytest.raises(ConflictError):
        await usecase.execute(team_uuid="abc", member_id=20)

    # The owner is never removed from the default team.
    mock_member_service.remove_team_member.assert_not_called()


@pytest.mark.asyncio
async def test_remove_team_member_usecase_non_owner_removed_from_default_team():
    from src.modules.workforce.application.usecases.team.remove_team_member_usecase import (
        RemoveTeamMemberUseCase,
    )

    team = _make_team(id=10, is_default=True)

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    removed_member = _make_team_member(id=1, member_id=20)
    mock_member_service = AsyncMock()
    mock_member_service.remove_team_member = AsyncMock(return_value=removed_member)

    usecase = RemoveTeamMemberUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=mock_member_service,
        organization_member_reader=_make_org_member_reader(),
        member_role_reader=_make_member_role_reader(role="admin"),
        organization_id=10,
    )

    await usecase.execute(team_uuid="abc", member_id=20)

    # A non-owner is removed from the default team like any other team.
    mock_member_service.remove_team_member.assert_awaited_once_with(
        team_id=10, member_id=20, organization_id=10
    )


@pytest.mark.asyncio
async def test_remove_team_member_usecase_team_without_id_raises_delete_error():
    from src.modules.workforce.application.usecases.team.remove_team_member_usecase import (
        RemoveTeamMemberUseCase,
    )
    from src.shared.exceptions.base_exceptions import DeleteError

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=_make_team(id=None))

    usecase = RemoveTeamMemberUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=AsyncMock(),
        organization_member_reader=_make_org_member_reader(),
        member_role_reader=_make_member_role_reader(),
        organization_id=10,
    )

    with pytest.raises(DeleteError):
        await usecase.execute(team_uuid="abc", member_id=20)


# --------------------------- SetTeamMemberRoleUseCase ---------------------------


@pytest.mark.asyncio
async def test_set_team_member_role_usecase_assigns_role():
    from src.modules.workforce.application.usecases.team.set_team_member_role_usecase import (
        SetTeamMemberRoleUseCase,
    )

    team = _make_team(id=10)
    promoted = _make_team_member(role="team_lead")

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    mock_member_service = AsyncMock()
    mock_member_service.set_member_role = AsyncMock(return_value=promoted)

    usecase = SetTeamMemberRoleUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=mock_member_service,
        organization_member_reader=_make_org_member_reader(),
        organization_id=10,
    )

    with patch(
        "src.modules.workforce.application.usecases.team.set_team_member_role_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result = await usecase.execute(
            team_uuid="abc", member_id=20, role="team_lead", actor_id=7
        )

        assert result is promoted
        mock_member_service.set_member_role.assert_awaited_once_with(
            team_id=10,
            member_id=20,
            role="team_lead",
            organization_id=10,
            actor_id=7,
        )


@pytest.mark.asyncio
async def test_set_team_member_role_usecase_supervisor():
    from src.modules.workforce.application.usecases.team.set_team_member_role_usecase import (
        SetTeamMemberRoleUseCase,
    )

    team = _make_team(id=10)
    supervisor = _make_team_member(role="supervisor")

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=team)

    mock_member_service = AsyncMock()
    mock_member_service.set_member_role = AsyncMock(return_value=supervisor)

    usecase = SetTeamMemberRoleUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=mock_member_service,
        organization_member_reader=_make_org_member_reader(),
        organization_id=10,
    )

    with patch(
        "src.modules.workforce.application.usecases.team.set_team_member_role_usecase.mediator"
    ) as mediator_mock:
        mediator_mock.publish = AsyncMock()
        result = await usecase.execute(
            team_uuid="abc", member_id=20, role="supervisor", actor_id=7
        )

        assert result is supervisor
        mock_member_service.set_member_role.assert_awaited_once_with(
            team_id=10,
            member_id=20,
            role="supervisor",
            organization_id=10,
            actor_id=7,
        )


@pytest.mark.asyncio
async def test_set_team_member_role_usecase_team_without_id_raises_update_error():
    from src.modules.workforce.application.usecases.team.set_team_member_role_usecase import (
        SetTeamMemberRoleUseCase,
    )
    from src.shared.exceptions.base_exceptions import UpdateError

    mock_team_service = AsyncMock()
    mock_team_service.get_team_by_uuid = AsyncMock(return_value=_make_team(id=None))

    usecase = SetTeamMemberRoleUseCase(
        team_domain_service=mock_team_service,
        team_member_domain_service=AsyncMock(),
        organization_member_reader=_make_org_member_reader(),
        organization_id=10,
    )

    with pytest.raises(UpdateError):
        await usecase.execute(
            team_uuid="abc", member_id=20, role="team_lead", actor_id=7
        )
