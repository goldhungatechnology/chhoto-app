from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin


class InvitationStatus:
    """
    Allowed status values for an invitation. Kept as constants (not an Enum)
    to match the string-typed status convention already used by other entities
    in this codebase (e.g. OrganizationEntity.status).
    """

    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"

    ALL: ClassVar[set[str]] = {PENDING, ACCEPTED, EXPIRED, REVOKED}


@dataclass(kw_only=True)
class InvitationEntity(BaseEntity, AuditMixin):
    """
    Entity representing an invitation to join an organization.

    `hashed_token` stores a deterministic SHA256 hash of the raw token sent to
    the invitee via email. The raw token never lives in the database; it is
    re-hashed at lookup time to find the matching row.
    """

    organization_id: int = field(
        metadata={
            "description": "The organization the invitee is being invited to",
            "index": True,
            "on_delete": "cascade",
        }
    )
    email: str = field(
        metadata={
            "description": "Email address being invited; case-insensitive match at accept-time",
            "index": True,
        }
    )
    role_id: int = field(
        metadata={
            "description": "Role to assign on acceptance",
            "on_delete": "restrict",
        }
    )
    team_id: int | None = field(
        default=None,
        metadata={
            "description": "Optional team to add the new member to on acceptance",
            "on_delete": "set null",
        },
    )
    invited_by_id: int = field(
        metadata={
            "description": "User id of the admin who issued the invitation",
            "on_delete": "set null",
        }
    )
    hashed_token: str = field(
        metadata={
            "description": "Deterministic hash of the invitation token; raw token is never stored",
            "unique": True,
            "index": True,
        }
    )
    status: str = field(
        default=InvitationStatus.PENDING,
        metadata={
            "description": "Invitation lifecycle status",
            "index": True,
        },
    )
    expires_at: datetime = field(
        metadata={"description": "Hard expiry timestamp (UTC)"}
    )
    accepted_at: datetime | None = field(
        default=None,
        metadata={"description": "Timestamp at which the invitation was accepted"},
    )

    # ---------------------- Queries / invariants ----------------------

    def is_pending(self) -> bool:
        """
        True iff the invitation is still pending — i.e. it has not yet been
        """
        return self.status == InvitationStatus.PENDING

    def is_revoked(self) -> bool:
        """
        True iff the invitation has been revoked by an admin. Revoked invites
        """
        return self.status == InvitationStatus.REVOKED

    def is_accepted(self) -> bool:
        """
        True iff the invitation has been accepted by the invitee. Accepted
        """
        return self.status == InvitationStatus.ACCEPTED

    def is_expired(self, *, now: datetime | None = None) -> bool:
        """
        True iff the expiry timestamp is in the past. Independent of the
        persisted status field: status may still be 'pending' on an expired
        row until a sweep flips it.
        """
        current = now or datetime.now(UTC)
        return self.expires_at <= current

    def is_acceptable(self, *, now: datetime | None = None) -> bool:
        """
        True only when the invitation is still actively claimable.
        """
        return self.is_pending() and not self.is_expired(now=now)

    def matches_email(self, email: str) -> bool:
        """
        Case-insensitive comparison of the invitee email to the supplied one.
        """
        if email is None:
            return False
        return self.email.strip().lower() == email.strip().lower()

    # ---------------------- State transitions ----------------------

    def mark_accepted(self, *, now: datetime | None = None) -> None:
        """
        Mark the invitation as accepted, setting the accepted_at timestamp to now.
        """
        self.status = InvitationStatus.ACCEPTED
        self.accepted_at = now or datetime.now(UTC)

    def mark_revoked(self) -> None:
        """
        Mark the invitation as revoked by an admin. Revoked invitations cannot be
        """
        self.status = InvitationStatus.REVOKED

    def mark_expired(self) -> None:
        """
        Mark the invitation as expired. Expired invitations cannot be accepted;
        """
        self.status = InvitationStatus.EXPIRED
