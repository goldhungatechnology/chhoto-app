from abc import ABC, abstractmethod


class MemberRoleReader(ABC):
    """
    Reader port for fetching role names associated with organization members.
    Used by the organization module to read role data from the workforce
    (RBAC) bounded context without direct repository coupling.
    """

    @abstractmethod
    async def get_member_roles(self, member_ids: list[int]) -> dict[int, str | None]:
        """
        Returns a dict mapping member_id -> role_name for the given member IDs.
        Members without an assigned role will have a None value.
        """
