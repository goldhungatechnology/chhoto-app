from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.audit.domain.services.audit_log_domain_service import (
    AuditLogDomainService,
)
from src.modules.audit.infrastructure.repositories.audit_log_repository_impl import (
    AuditLogRepositoryImpl,
)


class AuditContainer(containers.DeclarativeContainer):
    """
    Container for audit-related dependencies.
    """

    config = providers.Configuration()
    session = providers.Dependency(instance_of=AsyncSession)

    audit_log_repository = providers.Factory(AuditLogRepositoryImpl, session=session)
    audit_log_domain_service = providers.Factory(
        AuditLogDomainService, repository=audit_log_repository
    )


def get_audit_container(session: AsyncSession) -> AuditContainer:
    """
    Dependency injector for Audit container.
    """
    audit_container = AuditContainer()
    audit_container.session.override(session)
    return audit_container
