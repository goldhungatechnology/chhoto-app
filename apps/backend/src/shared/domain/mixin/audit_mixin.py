from dataclasses import dataclass


@dataclass
class AuditMixin:
    """
    Mixin to add audit fields to entities.
    """

    created_by_id: int | None = None
    updated_by_id: int | None = None

    def set_created_by(self, user_id: int):
        """
        Set the ID of the user who created the entity.
        """
        self.created_by_id = user_id

    def set_updated_by(self, user_id: int):
        """
        Set the ID of the user who last updated the entity.
        """
        self.updated_by_id = user_id
