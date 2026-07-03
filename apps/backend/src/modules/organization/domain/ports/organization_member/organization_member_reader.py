from abc import ABC, abstractmethod

from src.modules.organization.domain.entities.organization_member_entity import (
    OrganizationMemberEntity,
)


class OrganizationMemberReader(ABC):
    """
    Organization member reader port for cross-module reads of organization
    member data (used by other bounded contexts that need to resolve a
    `member_id` to the underlying user).
    """

    @abstractmethod
    async def get_members_by_ids(
        self, member_ids: list[int]
    ) -> list[OrganizationMemberEntity]:
        """
        Retrieves organization members for the given list of internal member IDs.
        """

    @abstractmethod
    async def get_member_by_user_id(
        self, organization_id: int, user_id: int
    ) -> OrganizationMemberEntity | None:
        """
        Resolves the active membership row for a user within an organization,
        or None if the user is not an active member.
        """

    @abstractmethod
    async def get_members_by_user_ids(
        self, organization_id: int, user_ids: list[int]
    ) -> list[OrganizationMemberEntity]:
        """
        Resolves the active membership rows for a list of users within an
        organization in a single query. Users without an active membership are
        simply omitted from the result.
        """

    @abstractmethod
    async def get_member_by_uuids(
        self, organization_id: int, member_uuid: str
    ) -> OrganizationMemberEntity | None:
        """
        Resolves the active membership rows for a list of member UUIDs within an
        organization in a single query. Members without an active membership are
        simply omitted from the result.
        """
