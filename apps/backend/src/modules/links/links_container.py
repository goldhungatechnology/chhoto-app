from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.links.application.usecases.create_link_usecase import CreateLinkUseCase
from src.modules.links.application.usecases.list_links_usecase import ListLinksUseCase
from src.modules.links.domain.services.link_domain_service import LinkDomainService
from src.modules.links.domain.services.link_session_domain_service import (
    LinkSessionDomainService,
)
from src.modules.links.infrastructure.repositories.link_repository_impl import (
    LinkRepositoryImpl,
)
from src.modules.links.infrastructure.repositories.link_session_repository_impl import (
    LinkSessionRepositoryImpl,
)


class LinksContainer(containers.DeclarativeContainer):
    """
    Container for links-related dependencies.
    """

    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)

    ## ---------------------------- Repositories ----------------------------
    link_repository = providers.Factory(LinkRepositoryImpl, session=session)
    link_session_repository = providers.Factory(
        LinkSessionRepositoryImpl, session=session
    )

    ## ---------------------------- Domain Services ----------------------------
    link_domain_service = providers.Factory(
        LinkDomainService,
        repository=link_repository,
    )
    link_session_domain_service = providers.Factory(
        LinkSessionDomainService,
        repository=link_session_repository,
    )

    ## ---------------------------- Use Cases ----------------------------
    create_link_usecase = providers.Factory(
        CreateLinkUseCase,
        link_domain_service=link_domain_service,
    )

    list_links_usecase = providers.Factory(
        ListLinksUseCase,
        link_domain_service=link_domain_service,
    )


def get_links_container(session: AsyncSession) -> LinksContainer:
    """
    Dependency injector for Links Container.
    """
    links_container = LinksContainer()
    links_container.session.override(session)
    return links_container
