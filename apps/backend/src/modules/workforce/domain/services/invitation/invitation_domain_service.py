from datetime import UTC, datetime, timedelta

from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
    InvitationStatus,
)
from src.modules.workforce.domain.events.invitation.invitation_domain_events import (
    InvitationCreatedEvent,
    InvitationResentEvent,
    InvitationRevokedEvent,
)
from src.modules.workforce.domain.repositories.invitation.invitation_repository import (
    IInvitationRepository,
)
from src.modules.workforce.domain.services.invitation.invitation_token_service import (
    InvitationTokenService,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DomainError,
    InvalidError,
    NotFoundError,
    ServerError,
)

INVITATION_TTL = timedelta(days=7)


class InvitationDomainService:
    """
    Domain logic for invitations: lifecycle transitions, re-invitation,
    revocation, expiry detection. Token generation and hashing are delegated
    to an injected `InvitationTokenService` so the domain stays free of
    concrete RNG / hash dependencies.
    """

    def __init__(
        self,
        repository: IInvitationRepository,
        token_service: InvitationTokenService,
    ):
        self.repository = repository
        self.token_service = token_service

    # ---------------------- Create ----------------------

    async def create_invitation(
        self,
        *,
        organization_id: int,
        email: str,
        role_id: int,
        team_id: int | None,
        invited_by_id: int,
        ttl: timedelta = INVITATION_TTL,
    ) -> tuple[InvitationEntity, str]:
        """
        Create a new invitation. Returns the persisted entity AND the raw
        token (so the caller can deliver it via email — the raw token is not
        recoverable from the database).

        Re-invitation policy: if a pending invitation already exists for the
        same (organization_id, email) it is revoked and a fresh one issued.
        """
        try:
            normalized_email = email.strip().lower()
            now = datetime.now(UTC)

            existing_pending = await self.repository.get_by(
                email=normalized_email,
                status=InvitationStatus.PENDING,
            )
            if existing_pending and existing_pending.id:
                existing_pending.mark_revoked()
                await self.repository.update(existing_pending)

            raw_token = self.token_service.generate_raw()
            hashed = self.token_service.hash(raw_token)

            invitation = InvitationEntity(
                organization_id=organization_id,
                email=normalized_email,
                role_id=role_id,
                team_id=team_id,
                invited_by_id=invited_by_id,
                hashed_token=hashed,
                status=InvitationStatus.PENDING,
                expires_at=now + ttl,
                created_by_id=invited_by_id,
            )

            persisted = await self.repository.add(invitation)
            if not persisted or not persisted.id:
                raise ServerError(error="Failed to create invitation")

            persisted.add_event(
                InvitationCreatedEvent(
                    invitation_id=persisted.id,
                    organization_id=persisted.organization_id,
                    email=persisted.email,
                    raw_token=raw_token,
                    expires_at=persisted.expires_at,
                )
            )

            return persisted, raw_token
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to create invitation", internal_details=str(e)
            ) from e

    # ---------------------- Lookup ----------------------

    async def get_by_raw_token(self, raw_token: str) -> InvitationEntity:
        """
        Resolve an invitation from the raw token. Returns the entity regardless
        of status; callers must enforce status / expiry rules.
        """
        if not raw_token:
            raise NotFoundError(error="Invitation not found")

        invitation = await self.repository.get_by_hashed_token(
            self.token_service.hash(raw_token)
        )
        if not invitation:
            raise NotFoundError(error="Invitation not found")
        return invitation

    async def get_by_uuid(self, invitation_uuid: str) -> InvitationEntity:
        invitation = await self.repository.get_by_uuid(invitation_uuid)
        if not invitation:
            raise NotFoundError(error="Invitation not found")
        return invitation

    async def list_for_organization(
        self, *, status: str | None = None
    ) -> list[InvitationEntity]:
        try:
            criteria = {}
            if status is not None:
                if status not in InvitationStatus.ALL:
                    raise InvalidError(error=f"Unknown invitation status: {status}")
                criteria["status"] = status
            return await self.repository.filter(**criteria)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to list invitations", internal_details=str(e)
            ) from e

    # ---------------------- Validation ----------------------

    def ensure_acceptable(
        self,
        invitation: InvitationEntity,
        *,
        accepting_email: str,
        now: datetime | None = None,
    ) -> None:
        """
        Centralized validation for the accept flow. Raises a DomainError if
        the invitation cannot be accepted for any reason; succeeds silently
        otherwise.
        """
        if invitation.is_revoked():
            raise InvalidError(error="Invitation has been revoked")
        if invitation.is_accepted():
            raise ConflictError(error="Invitation has already been accepted")
        if invitation.status == InvitationStatus.EXPIRED:
            raise InvalidError(error="Invitation has expired")
        if invitation.is_expired(now=now):
            raise InvalidError(error="Invitation has expired")
        if not invitation.is_pending():
            raise InvalidError(error="Invitation is not in a pending state")
        if not invitation.matches_email(accepting_email):
            raise InvalidError(
                error="This invitation was sent to a different email address"
            )

    # ---------------------- State transitions ----------------------

    async def mark_as_accepted(self, invitation: InvitationEntity) -> InvitationEntity:
        try:
            if not invitation.id:
                raise ServerError(error="Cannot accept an unsaved invitation")

            # Atomic compare-and-set: only succeeds if the invitation is still
            # 'pending'. A concurrent accept of the same invitation gets None
            # here and is rejected, preventing duplicate memberships.
            updated = await self.repository.mark_accepted_if_pending(invitation.id)
            if not updated or not updated.id:
                raise ConflictError(
                    error="This invitation has already been accepted or is no longer valid"
                )
            return updated
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to mark invitation as accepted",
                internal_details=str(e),
            ) from e

    async def revoke(self, invitation_uuid: str) -> InvitationEntity:
        try:
            invitation = await self.get_by_uuid(invitation_uuid)

            if invitation.is_accepted():
                raise ConflictError(error="Accepted invitations cannot be revoked")
            if invitation.is_revoked():
                return invitation

            invitation.mark_revoked()
            invitation.mark_updated()
            updated = await self.repository.update(invitation)
            if not updated or not updated.id:
                raise ServerError(error="Failed to revoke invitation")

            updated.add_event(
                InvitationRevokedEvent(
                    invitation_id=updated.id,
                    organization_id=updated.organization_id,
                )
            )
            return updated
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to revoke invitation", internal_details=str(e)
            ) from e

    async def resend(
        self, invitation_uuid: str, *, actor_id: int
    ) -> tuple[InvitationEntity, str]:
        """
        Resend an invitation: revoke the existing row and create a fresh one
        with a new token and a fresh TTL. Returns the new invitation and the
        new raw token.
        """
        try:
            old = await self.get_by_uuid(invitation_uuid)
            if old.is_accepted():
                raise ConflictError(error="Accepted invitations cannot be resent")

            if old.is_pending() and old.id:
                old.mark_revoked()
                old.mark_updated()
                await self.repository.update(old)

            new_invite, raw_token = await self.create_invitation(
                organization_id=old.organization_id,
                email=old.email,
                role_id=old.role_id,
                team_id=old.team_id,
                invited_by_id=actor_id,
            )

            if not new_invite.id or not old.id:
                raise ServerError(error="Failed to resend invitation")

            # Swap the CreatedEvent for a ResentEvent so listeners can
            # differentiate "first-time send" from "resend".
            new_invite.pull_events()
            new_invite.add_event(
                InvitationResentEvent(
                    old_invitation_id=old.id,
                    new_invitation_id=new_invite.id,
                    organization_id=new_invite.organization_id,
                    email=new_invite.email,
                    raw_token=raw_token,
                    expires_at=new_invite.expires_at,
                )
            )
            return new_invite, raw_token
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to resend invitation", internal_details=str(e)
            ) from e
