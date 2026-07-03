from src.modules.audit.domain.entities.audit_log_entity import AuditLogEntity
from src.modules.audit.domain.repositories.audit_log_repository import (
    IAuditLogRepository,
)
from src.shared.exceptions.base_exceptions import CreateError, DomainError


class AuditLogDomainService:
    """
    Service for audit event persistence/query behavior.
    """

    def __init__(self, repository: IAuditLogRepository):
        self.repository = repository

    async def create_audit_log(self, audit_log: AuditLogEntity) -> AuditLogEntity:
        """
        create audit log
        """
        try:
            return await self.repository.add(audit_log)
        except DomainError:
            raise
        except Exception as e:
            raise CreateError(
                error="Failed to create audit log",
                internal_details=str(e),
            ) from e

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
        list audit events with filters for a specific organization
        """
        return await self.repository.list_events(
            organization_id=organization_id,
            action=action,
            entity_table=entity_table,
            actor_id=actor_id,
            limit=limit,
            offset=offset,
        )
