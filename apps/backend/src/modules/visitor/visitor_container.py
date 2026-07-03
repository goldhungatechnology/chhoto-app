from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organization.infrastructure.services.organization_reader_impl import (
    get_organization_reader,
)
from src.modules.visitor.application.usecases.end_visitor_session_usecase import (
    EndVisitorSessionUseCase,
)
from src.modules.visitor.application.usecases.get_active_visitors_usecase import (
    GetActiveVisitorsUseCase,
)
from src.modules.visitor.application.usecases.start_visitor_session_usecase import (
    StartVisitorSessionUseCase,
)
from src.modules.visitor.application.usecases.track_page_enter_usecase import (
    TrackPageEnterUseCase,
)
from src.modules.visitor.application.usecases.visitor_heartbeat_usecase import (
    VisitorHeartbeatUseCase,
)
from src.modules.visitor.application.usecases.update_visitor_identity_usecase import (
    UpdateVisitorIdentityUseCase,
)
from src.modules.visitor.application.usecases.list_visitors_usecase import (
    ListVisitorsUseCase,
)
from src.modules.visitor.application.usecases.get_visitors_by_country_usecase import (
    GetVisitorsByCountryUseCase,
)
from src.modules.visitor.application.usecases.get_top_pages_usecase import (
    GetTopPagesUseCase,
)
from src.modules.visitor.domain.services.visitor_domain_service import (
    VisitorDomainService,
)
from src.modules.visitor.domain.services.visitor_page_visit_domain_service import (
    VisitorPageVisitDomainService,
)
from src.modules.visitor.domain.services.visitor_session_domain_service import (
    VisitorSessionDomainService,
)
from src.modules.visitor.infrastructure.cache.visitor_presence_cache_service import (
    VisitorPresenceCacheService,
)
from src.modules.visitor.infrastructure.repositories.visitor_page_visit_repository_impl import (
    VisitorPageVisitRepositoryImpl,
)
from src.modules.visitor.infrastructure.repositories.visitor_repository_impl import (
    VisitorRepositoryImpl,
)
from src.modules.visitor.infrastructure.repositories.visitor_session_repository_impl import (
    VisitorSessionRepositoryImpl,
)
from src.modules.visitor.infrastructure.services.visitor_presence_notifier_impl import (
    VisitorPresenceNotifierImpl,
)


class VisitorContainer(containers.DeclarativeContainer):
    """
    Container for visitor-related dependencies.
    """

    config = providers.Configuration()
    session = providers.Dependency(instance_of=AsyncSession)

    ## ------------------------ Cross-module ports ------------------------ ##

    organization_reader = providers.Factory(get_organization_reader, session=session)

    ## ------------------------ Repositories ------------------------ ##

    visitor_repository = providers.Factory(VisitorRepositoryImpl, session=session)
    visitor_session_repository = providers.Factory(
        VisitorSessionRepositoryImpl, session=session
    )
    visitor_page_visit_repository = providers.Factory(
        VisitorPageVisitRepositoryImpl, session=session
    )

    ## ------------------------ Real-time (Redis / WS) ------------------------ ##

    presence_store = providers.Factory(VisitorPresenceCacheService)
    presence_notifier = providers.Factory(VisitorPresenceNotifierImpl)

    ## ------------------------ Domain Services ------------------------ ##

    visitor_domain_service = providers.Factory(
        VisitorDomainService, repository=visitor_repository
    )
    visitor_session_domain_service = providers.Factory(
        VisitorSessionDomainService, repository=visitor_session_repository
    )
    visitor_page_visit_domain_service = providers.Factory(
        VisitorPageVisitDomainService, repository=visitor_page_visit_repository
    )

    ## ------------------------ Use Cases ------------------------ ##

    start_visitor_session_usecase = providers.Factory(
        StartVisitorSessionUseCase,
        organization_reader=organization_reader,
        visitor_domain_service=visitor_domain_service,
        visitor_session_domain_service=visitor_session_domain_service,
        visitor_page_visit_domain_service=visitor_page_visit_domain_service,
        presence_store=presence_store,
        presence_notifier=presence_notifier,
    )

    track_page_enter_usecase = providers.Factory(
        TrackPageEnterUseCase,
        visitor_session_domain_service=visitor_session_domain_service,
        visitor_page_visit_domain_service=visitor_page_visit_domain_service,
        visitor_domain_service=visitor_domain_service,
        presence_store=presence_store,
        presence_notifier=presence_notifier,
    )

    visitor_heartbeat_usecase = providers.Factory(
        VisitorHeartbeatUseCase,
        presence_store=presence_store,
        visitor_session_domain_service=visitor_session_domain_service,
        visitor_domain_service=visitor_domain_service,
        presence_notifier=presence_notifier,
    )

    end_visitor_session_usecase = providers.Factory(
        EndVisitorSessionUseCase,
        visitor_session_domain_service=visitor_session_domain_service,
        visitor_page_visit_domain_service=visitor_page_visit_domain_service,
        presence_store=presence_store,
        presence_notifier=presence_notifier,
    )

    get_active_visitors_usecase = providers.Factory(
        GetActiveVisitorsUseCase, presence_store=presence_store
    )

    update_visitor_identity_usecase = providers.Factory(
        UpdateVisitorIdentityUseCase,
        visitor_repository=visitor_repository,
        presence_store=presence_store,
        presence_notifier=presence_notifier,
    )

    list_visitors_usecase = providers.Factory(
        ListVisitorsUseCase,
        visitor_repository=visitor_repository,
        visitor_session_repository=visitor_session_repository,
        visitor_page_visit_repository=visitor_page_visit_repository,
    )

    get_visitors_by_country_usecase = providers.Factory(
        GetVisitorsByCountryUseCase,
        visitor_repository=visitor_repository,
        visitor_session_repository=visitor_session_repository,
    )

    get_top_pages_usecase = providers.Factory(
        GetTopPagesUseCase,
        visitor_repository=visitor_repository,
        visitor_page_visit_repository=visitor_page_visit_repository,
    )


def get_visitor_container(session: AsyncSession) -> VisitorContainer:
    """
    Dependency injector for the Visitor Container.
    """
    visitor_container = VisitorContainer()
    visitor_container.session.override(session)
    return visitor_container
