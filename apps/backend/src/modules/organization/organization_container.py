from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.user.user_reader_impl import get_user_reader_impl
from src.modules.organization.application.usecases.core.create_organization_usecase import (
    CreateOrganizationUseCase,
)
from src.modules.organization.application.usecases.core.list_organization_members_usecase import (
    ListOrganizationMembersUseCase,
)
from src.modules.organization.infrastructure.services.member_role_reader_impl import (
    MemberRoleReaderImpl,
)
from src.modules.organization.application.usecases.core.edit_organization_details_usecase import (
    EditOrganizationDetailsUseCase,
)
from src.modules.organization.application.usecases.core.get_organization_details_usecase import (
    GetOrganizationDetailsUseCase,
)
from src.modules.organization.application.usecases.core.switch_organization_usecase import (
    SwitchOrganizationUseCase,
)
from src.modules.organization.domain.services.organization_domain_service import (
    OrganizationDomainService,
)
from src.modules.organization.domain.services.organization_member_domain_service import (
    OrganizationMemberDomainService,
)
from src.modules.organization.domain.services.organization_onboarding_domain_service import (
    OrganizationOnboardingDomainService,
)
from src.modules.organization.domain.services.organization_media_domain_service import (
    OrganizationMediaDomainService,
)
from src.modules.organization.infrastructure.repositories.organization_member_repository_impl import (
    OrganizationMemberRepositoryImpl,
)
from src.modules.organization.infrastructure.repositories.organization_onboarding_repository_impl import (
    OrganizationOnboardingRepositoryImpl,
)
from src.modules.organization.infrastructure.repositories.organization_repository_impl import (
    OrganizationRepositoryImpl,
)

# Organization Media Repository
from src.modules.organization.infrastructure.repositories.organization_media_repository_impl import (
    OrganizationMediaRepositoryImpl,
)


class OrganizationContainer(containers.DeclarativeContainer):
    """
    Container for organization-related dependencies.
    """

    config = providers.Configuration()
    session = providers.Dependency(instance_of=AsyncSession)

    ## ------------------------ Cross-module ports ------------------------ ##

    user_reader = providers.Factory(get_user_reader_impl)

    ## ------------------------ Readers ------------------------ ##

    member_role_reader = providers.Factory(
        MemberRoleReaderImpl,
        session=session,
    )

    ## ------------------------ Repositories ------------------------ ##

    organization_repository = providers.Factory(
        OrganizationRepositoryImpl, session=session
    )
    organization_member_repository = providers.Factory(
        OrganizationMemberRepositoryImpl, session=session
    )
    organization_onboarding_repository = providers.Factory(
        OrganizationOnboardingRepositoryImpl, session=session
    )
    organization_media_repository = providers.Factory(
        OrganizationMediaRepositoryImpl, session=session
    )

    ## ------------------------ Domain Services ------------------------ ##

    organization_domain_service = providers.Factory(
        OrganizationDomainService,
        repository=organization_repository,
    )
    organization_member_domain_service = providers.Factory(
        OrganizationMemberDomainService,
        repository=organization_member_repository,
    )
    organization_onboarding_domain_service = providers.Factory(
        OrganizationOnboardingDomainService,
        repository=organization_onboarding_repository,
    )
    organization_media_domain_service = providers.Factory(
        OrganizationMediaDomainService,
        repository=organization_media_repository,
    )

    ## ------------------------ Use Cases ------------------------ ##

    create_organization_usecase = providers.Factory(
        CreateOrganizationUseCase,
        organization_domain_service=organization_domain_service,
        organization_member_domain_service=organization_member_domain_service,
        organization_onboarding_domain_service=organization_onboarding_domain_service,
    )

    get_organization_details_usecase = providers.Factory(
        GetOrganizationDetailsUseCase,
        organization_domain_service=organization_domain_service,
        organization_media_domain_service=organization_media_domain_service,
    )

    switch_organization_usecase = providers.Factory(
        SwitchOrganizationUseCase,
        organization_domain_service=organization_domain_service,
    )

    edit_organization_usecase = providers.Factory(
        EditOrganizationDetailsUseCase,
        organization_domain_service=organization_domain_service,
        organization_media_domain_service=organization_media_domain_service,
    )

    list_organization_members_usecase = providers.Factory(
        ListOrganizationMembersUseCase,
        organization_member_domain_service=organization_member_domain_service,
        user_reader=user_reader,
        member_role_reader=member_role_reader,
    )


def get_organization_container(session: AsyncSession) -> OrganizationContainer:
    """
    Dependency injector for Organization Container
    """
    organization_container = OrganizationContainer()
    organization_container.session.override(session)
    return organization_container
