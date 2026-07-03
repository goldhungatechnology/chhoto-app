from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality to entities.
    """

    deleted_at: datetime | None = None

    def soft_delete(self):
        """
        soft delete the entity
        """

        self.deleted_at = datetime.now(UTC)

    def restore(self):
        """
        restore the entity
        """
        self.deleted_at = None
