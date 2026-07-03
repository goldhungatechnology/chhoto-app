from typing import Literal
from src.shared.schemas import BaseSchema, Field, computed_field


class CreatedByUserSchema(BaseSchema):
    """
    Schema for the user who created the role.
    """

    uuid: str
    email: str
    avatar_bg: str
    full_name: str | None
    avatar: str | None
    is_online: bool = False

    model_config = {
        "from_attributes": True,
    }


class RoleResponseSchema(BaseSchema):
    """
    Schema for listing roles response.
    """

    uuid: str
    name: str
    description: str | None
    created_by: CreatedByUserSchema | None

    is_system_role: bool = Field(exclude=True)

    @computed_field()
    @property
    def status(self) -> Literal["system", "custom"]:
        """
        Computed field to determine if the role is a system role or a custom role.
        """
        return "system" if self.is_system_role else "custom"

    model_config = {
        "from_attributes": True,
    }


class CreateRoleRequestSchema(BaseSchema):
    """
    Schema for creating a new role request.
    """

    name: str
    description: str


class PermissionResponseSchema(BaseSchema):
    """
    Schema for listing permissions response.
    """

    uuid: str
    name: str
    key: str
    description: str | None
    category: str
    created_by: CreatedByUserSchema | None

    is_system_permission: bool = Field(exclude=True)

    @computed_field()
    @property
    def status(self) -> Literal["system", "custom"]:
        """
        Computed field to determine if the permission is a system permission or a custom permission.
        """
        return "system" if self.is_system_permission else "custom"

    model_config = {
        "from_attributes": True,
    }
