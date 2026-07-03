from dataclasses import dataclass, field

from src.shared.domain.entity.base_entity import BaseEntity
from src.shared.domain.mixin.audit_mixin import AuditMixin
from src.shared.domain.mixin.soft_delete_mixin import SoftDeleteMixin


@dataclass(kw_only=True)
class TeamEntity(BaseEntity, AuditMixin, SoftDeleteMixin):
    """
    Entity representing a team within an organization.
    """

    _TEAM_COLORS = [
        "default",
        "secondary",
        "success",
        "info",
        "warning",
        "magenta",
    ]  ## since frontend needs these values instead of hex code
    _INDEX = 0

    name: str = field(
        metadata={
            "description": "The name of the team",
        }
    )
    description: str | None = field(
        default=None,
        metadata={"description": "A brief description of the team"},
    )
    color: str | None = field(
        default=None,
        metadata={"description": "A color identifier used in the UI for the team"},
    )
    timezone: str | None = field(
        default=None,
        metadata={"description": "The default timezone associated with the team"},
    )
    is_default: bool = field(
        default=False,
        metadata={
            "description": "Indicates whether this is the organization's default team"
        },
    )
    status: str = field(
        default="active",
        metadata={"description": "The current status of the team"},
    )

    organization_id: int = field(
        metadata={
            "description": "The ID of the organization this team belongs to",
            "index": True,
            "on_delete": "cascade",
        }
    )

    def is_active(self) -> bool:
        """
        Check if the team is active (not soft-deleted).
        """
        return self.deleted_at is None

    def mark_as_default(self) -> None:
        """
        Mark this team as the organization's default team.
        """
        self.is_default = True

    def unmark_as_default(self) -> None:
        """
        Remove the default flag from this team.
        """
        self.is_default = False

    @classmethod
    def get_random_color(cls) -> str:
        """
        Generate a random color in hexadecimal format.
        """
        color = cls._TEAM_COLORS[cls._INDEX]
        cls._INDEX = (cls._INDEX + 1) % len(cls._TEAM_COLORS)
        return color
