from dataclasses import dataclass


@dataclass
class TenantMixin:
    """
    Mixin to add tenant (organization) isolation to entities.
    """

    organization_id: int | None = None

    def set_organization(self, organization_id: int):
        """
        Set the organization ID for tenant isolation.
        """
        self.organization_id = organization_id
