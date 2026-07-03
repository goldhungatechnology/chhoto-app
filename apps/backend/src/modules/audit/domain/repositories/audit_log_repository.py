from src.modules.audit.domain.entities.audit_log_entity import AuditLogEntity
from src.shared.domain.repository.base_repository_interface import IBaseRepository
from abc import abstractmethod


class IAuditLogRepository(IBaseRepository[AuditLogEntity]):
    """
    Interface for audit-log repository.
    """

    @abstractmethod
    async def list_events(
        self,
        *,
        organization_id: int,
        action: str | None = None,
        entity_table: str | None = None,
        actor_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AuditLogEntity], int]:
        """
        List audit events for an organization with filters and pagination.
        """
