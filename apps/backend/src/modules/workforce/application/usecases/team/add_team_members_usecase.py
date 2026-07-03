from collections.abc import Callable, Iterable

from src.modules.auth.domain.ports.user.user_reader import UserReader
from src.modules.organization.domain.ports.organization_member.organization_member_reader import (
    OrganizationMemberReader,
)
from src.modules.workforce.domain.entities.team.team_member_entity import (
    TeamMemberEntity,
    TeamMemberRole,
)
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.modules.workforce.domain.services.team.team_member_domain_service import (
    TeamMemberDomainService,
)
from src.shared.exceptions.base_exceptions import CreateError, DomainError, InvalidError
from src.shared.mediator.mediator import mediator

# Maps an internal team-member role to the request bucket it came from, so a
# validation error can be reported back under the same key the client sent.
_ROLE_TO_BUCKET = {
    TeamMemberRole.MEMBER: "member",
    TeamMemberRole.SUPERVISOR: "supervisor",
    TeamMemberRole.TEAM_LEAD: "lead",
}


class AddTeamMembersUseCase:
    """
    Use case for adding multiple members to a team in one request.

    Input is role-bucketed by user uuid: `members` and `supervisors` are lists
    of user uuids, `lead` is an optional single user uuid; all three are
    optional. Semantics:
      - every provided user is added as a NEW team member with the bucketed
        role (use the set-role endpoint to re-role an existing member);
      - assigning a lead enforces a single lead per team (any current lead is
        demoted to member);
      - validation is all-or-nothing: if any uuid is unknown, not an active
        member of the organization, or already on the team, nothing is written
        and the surrounding unit of work rolls back. Each failure is reported
        under the bucket the uuid was sent in, e.g.
        ``{"supervisor": "a@b.com is already on the team"}``.
    """

    def __init__(
        self,
        team_domain_service: TeamDomainService,
        team_member_domain_service: TeamMemberDomainService,
        organization_member_reader: OrganizationMemberReader,
        user_reader: UserReader,
        organization_id: int,
    ):
        self.team_domain_service = team_domain_service
        self.team_member_domain_service = team_member_domain_service
        self.organization_member_reader = organization_member_reader
        self.user_reader = user_reader
        self.organization_id = organization_id

    async def execute(
        self,
        *,
        team_uuid: str,
        members: list[str],
        supervisors: list[str],
        lead: str | None,
        actor_id: int,
    ) -> list[TeamMemberEntity]:
        """
        Executes the bulk add. Returns the team-member entities touched by the
        request (the newly added members and any demoted previous lead).
        """
        try:
            role_by_uuid = self._collect_roles(members, supervisors, lead)
            team_id = await self._resolve_team_id(team_uuid)

            member_id_by_uuid, email_by_uuid = await self._resolve_member_ids(
                role_by_uuid
            )

            existing = await self.team_member_domain_service.list_team_members(team_id)
            self._reject_existing(
                role_by_uuid, member_id_by_uuid, email_by_uuid, existing
            )

            # Newest entity per member_id, so a demoted-then-readded member is
            # reported once.
            touched: dict[int, TeamMemberEntity] = {}
            if lead is not None:
                touched.update(
                    await self._demote_current_lead(team_id, existing, actor_id)
                )
            touched.update(
                await self._add_members(
                    team_id, role_by_uuid, member_id_by_uuid, actor_id
                )
            )

            await self._publish_events(touched.values())
            return list(touched.values())
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to add team members", internal_details=str(e)
            ) from e

    # --------------------------- request parsing --------------------------- #

    def _collect_roles(
        self, members: list[str], supervisors: list[str], lead: str | None
    ) -> dict[str, str]:
        """
        Collapse the role buckets into one `{user_uuid: role}` map, rejecting a
        uuid that appears under more than one role and an empty request.
        """
        role_by_uuid: dict[str, str] = {}
        for uuid in members:
            self._assign(role_by_uuid, uuid, TeamMemberRole.MEMBER)
        for uuid in supervisors:
            self._assign(role_by_uuid, uuid, TeamMemberRole.SUPERVISOR)
        if lead is not None:
            self._assign(role_by_uuid, lead, TeamMemberRole.TEAM_LEAD)

        if not role_by_uuid:
            raise InvalidError(error="No team members provided")
        return role_by_uuid

    @staticmethod
    def _assign(target: dict[str, str], uuid: str, role: str) -> None:
        """
        Records `uuid -> role`, rejecting a uuid listed under multiple roles.
        """
        if uuid in target:
            raise InvalidError(
                error="A user was assigned more than one role",
                internal_details=f"duplicate user uuid in payload: {uuid}",
            )
        target[uuid] = role

    async def _resolve_team_id(self, team_uuid: str) -> int:
        """
        Resolve the team by uuid and return its id, failing if it has none.
        """
        team = await self.team_domain_service.get_team_by_uuid(team_uuid)
        if not team.id:
            raise CreateError(error="Team not found")
        return team.id

    # ----------------------------- resolution ----------------------------- #

    async def _resolve_member_ids(
        self, role_by_uuid: dict[str, str]
    ) -> tuple[dict[str, int], dict[str, str]]:
        """
        Resolve every uuid to the organization-member id used by the team
        membership row. Returns `(member_id_by_uuid, email_by_uuid)`.

        Fails all-or-nothing: a uuid that is not a known user, or whose user is
        not an active member of this organization, aborts the whole request with
        a per-bucket error.
        """
        uuids = list(role_by_uuid.keys())
        users = await self.user_reader.get_users_by_uuids(uuids)
        user_id_by_uuid = {u.uuid: u.id for u in users if u.id is not None}
        email_by_uuid = {u.uuid: u.email for u in users}

        missing = [u for u in uuids if u not in user_id_by_uuid]
        if missing:
            raise InvalidError(
                error="Some users could not be found",
                errors=self._bucket_errors(
                    missing, role_by_uuid, lambda items: self._not_found_message(items)
                ),
                internal_details=f"unknown user uuids: {missing}",
            )

        org_members = await self.organization_member_reader.get_members_by_user_ids(
            self.organization_id, list(user_id_by_uuid.values())
        )
        member_id_by_user_id = {
            om.user_id: om.id for om in org_members if om.id is not None
        }

        not_in_org = [
            uuid
            for uuid, user_id in user_id_by_uuid.items()
            if user_id not in member_id_by_user_id
        ]
        if not_in_org:
            raise InvalidError(
                error="Some users are not active members of this organization",
                errors=self._bucket_errors(
                    not_in_org,
                    role_by_uuid,
                    lambda items: self._join(
                        [email_by_uuid[u] for u in items],
                        "is not a member of this organization",
                        "are not members of this organization",
                    ),
                ),
                internal_details=f"user uuids not in org: {not_in_org}",
            )

        member_id_by_uuid = {
            uuid: member_id_by_user_id[user_id_by_uuid[uuid]] for uuid in role_by_uuid
        }
        return member_id_by_uuid, email_by_uuid

    def _reject_existing(
        self,
        role_by_uuid: dict[str, str],
        member_id_by_uuid: dict[str, int],
        email_by_uuid: dict[str, str],
        existing: list[TeamMemberEntity],
    ) -> None:
        """
        Reject any provided user that is already on the team, grouping the
        offending emails under the bucket the client sent them in.
        """
        existing_member_ids = {m.member_id for m in existing}
        already_on_team = [
            uuid
            for uuid in role_by_uuid
            if member_id_by_uuid[uuid] in existing_member_ids
        ]
        if already_on_team:
            raise InvalidError(
                error="Some users are already on the team",
                errors=self._bucket_errors(
                    already_on_team,
                    role_by_uuid,
                    lambda items: self._join(
                        [email_by_uuid[u] for u in items],
                        "is already on the team",
                        "are already on the team",
                    ),
                ),
            )

    # ------------------------------- writes ------------------------------- #

    async def _demote_current_lead(
        self, team_id: int, existing: list[TeamMemberEntity], actor_id: int
    ) -> dict[int, TeamMemberEntity]:
        """
        Demote any current team lead to member, enforcing a single lead. The
        incoming lead is guaranteed not to be on the team (rejected earlier).
        """
        demoted: dict[int, TeamMemberEntity] = {}
        for member in existing:
            if member.role == TeamMemberRole.TEAM_LEAD:
                entity = await self.team_member_domain_service.set_member_role(
                    team_id=team_id,
                    member_id=member.member_id,
                    role=TeamMemberRole.MEMBER,
                    organization_id=self.organization_id,
                    actor_id=actor_id,
                )
                demoted[entity.member_id] = entity
        return demoted

    async def _add_members(
        self,
        team_id: int,
        role_by_uuid: dict[str, str],
        member_id_by_uuid: dict[str, int],
        actor_id: int,
    ) -> dict[int, TeamMemberEntity]:
        """
        Add every provided user to the team as a new member with their role.
        """
        added: dict[int, TeamMemberEntity] = {}
        for uuid, role in role_by_uuid.items():
            entity = TeamMemberEntity(
                team_id=team_id,
                member_id=member_id_by_uuid[uuid],
                role=role,
                created_by_id=actor_id,
            )
            result = await self.team_member_domain_service.add_team_member(
                entity, organization_id=self.organization_id
            )
            added[result.member_id] = result
        return added

    @staticmethod
    async def _publish_events(entities: Iterable[TeamMemberEntity]) -> None:
        """
        Publish the domain events accumulated on every touched entity.
        """
        for entity in entities:
            for event in entity.pull_events():
                await mediator.publish(event)

    # ------------------------- error formatting ------------------------- #

    @staticmethod
    def _bucket_errors(
        uuids: list[str],
        role_by_uuid: dict[str, str],
        message_for: Callable[[list[str]], str],
    ) -> dict[str, str]:
        """
        Group offending uuids by their request bucket and build one message per
        bucket via `message_for` (which receives that bucket's uuids).
        """
        grouped: dict[str, list[str]] = {}
        for uuid in uuids:
            grouped.setdefault(_ROLE_TO_BUCKET[role_by_uuid[uuid]], []).append(uuid)
        return {bucket: message_for(items) for bucket, items in grouped.items()}

    @staticmethod
    def _join(values: list[str], singular: str, plural: str) -> str:
        """
        Join `values` and append the verb phrase matching their count, e.g.
        `["a@b.com"] -> "a@b.com is already on the team"`.
        """
        return f"{', '.join(values)} {singular if len(values) == 1 else plural}"

    @staticmethod
    def _not_found_message(items: list[str]) -> str:
        """
        Message for uuids that resolve to no user (no email to show).
        """
        return "user email not found" if len(items) == 1 else "users email not found"
