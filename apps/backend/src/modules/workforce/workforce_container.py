from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.user.user_provisioner_impl import (
    get_user_provisioner,
)
from src.modules.auth.infrastructure.user.user_reader_impl import get_user_reader_impl
from src.modules.organization.infrastructure.services.member_role_reader_impl import (
    get_member_role_reader,
)
from src.modules.organization.infrastructure.services.organization_member_reader_impl import (
    get_organization_member_reader,
)
from src.modules.organization.infrastructure.services.organization_membership_writer_impl import (
    get_organization_membership_writer,
)
from src.modules.organization.infrastructure.services.organization_reader_impl import (
    get_organization_reader,
)
from src.modules.workforce.application.usecases.invitation.accept_invitation_usecase import (
    AcceptInvitationUseCase,
)
from src.modules.workforce.application.usecases.invitation.create_invitation_usecase import (
    CreateInvitationUseCase,
)
from src.modules.workforce.application.usecases.invitation.get_invitation_by_token_usecase import (
    GetInvitationByTokenUseCase,
)
from src.modules.workforce.application.usecases.invitation.list_invitations_usecase import (
    ListInvitationsUseCase,
)
from src.modules.workforce.application.usecases.invitation.resend_invitation_usecase import (
    ResendInvitationUseCase,
)
from src.modules.workforce.application.usecases.invitation.revoke_invitation_usecase import (
    RevokeInvitationUseCase,
)
from src.modules.workforce.application.usecases.invitation.signup_and_accept_invitation_usecase import (
    SignupAndAcceptInvitationUseCase,
)
from src.modules.workforce.application.usecases.rbac.create_role_usecase import (
    CreateRoleUseCase,
)
from src.modules.workforce.application.usecases.rbac.list_permissions_usecase import (
    ListPermissionsUseCase,
)
from src.modules.workforce.application.usecases.rbac.list_roles_usecase import (
    ListRolesUseCase,
)
from src.modules.workforce.application.usecases.team.add_team_members_usecase import (
    AddTeamMembersUseCase,
)
from src.modules.workforce.application.usecases.team.create_team_usecase import (
    CreateTeamUseCase,
)
from src.modules.workforce.application.usecases.team.delete_team_usecase import (
    DeleteTeamUseCase,
)
from src.modules.workforce.application.usecases.team.get_team_usecase import (
    GetTeamUseCase,
)
from src.modules.workforce.application.usecases.team.list_team_members_usecase import (
    ListTeamMembersUseCase,
)
from src.modules.workforce.application.usecases.team.list_teams_usecase import (
    ListTeamsUseCase,
)
from src.modules.workforce.application.usecases.team.relocate_team_members_usecase import (
    RelocateTeamMembersUseCase,
)
from src.modules.workforce.application.usecases.team.remove_team_member_usecase import (
    RemoveTeamMemberUseCase,
)
from src.modules.workforce.application.usecases.team.set_team_member_role_usecase import (
    SetTeamMemberRoleUseCase,
)
from src.modules.workforce.application.usecases.team.update_team_usecase import (
    UpdateTeamUseCase,
)
from src.modules.workforce.domain.services.rbac.rbac_member_role_domain_service import (
    RbacMemberRoleDomainService,
)
from src.modules.workforce.domain.services.rbac.rbac_permission_domain_service import (
    RbacPermissionDomainService,
)
from src.modules.workforce.domain.services.rbac.rbac_role_domain_service import (
    RbacRoleDomainService,
)
from src.modules.workforce.domain.services.invitation.invitation_domain_service import (
    InvitationDomainService,
)
from src.modules.workforce.domain.services.team.team_domain_service import (
    TeamDomainService,
)
from src.modules.workforce.domain.services.team.team_member_domain_service import (
    TeamMemberDomainService,
)
from src.modules.workforce.infrastructure.repositories.invitation.invitation_repository_impl import (
    InvitationRepositoryImpl,
)
from src.modules.workforce.infrastructure.services.invitation.invitation_token_service_impl import (
    get_invitation_token_service,
)
from src.modules.workforce.infrastructure.repositories.rbac.rbac_member_role_repository_impl import (
    MemberRoleRepositoryImpl,
)
from src.modules.workforce.infrastructure.repositories.rbac.rbac_permission_repository_impl import (
    PermissionRepositoryImpl,
)
from src.modules.workforce.infrastructure.repositories.rbac.rbac_role_repository_impl import (
    RoleRepositoryImpl,
)
from src.modules.workforce.infrastructure.repositories.team.team_member_repository_impl import (
    TeamMemberRepositoryImpl,
)
from src.modules.workforce.infrastructure.repositories.team.team_repository_impl import (
    TeamRepositoryImpl,
)


class WorkforceContainer(containers.DeclarativeContainer):
    """
    WorkforceContainer is a dependency injection container for the workforce module.
    """

    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)
    organization_id = providers.Dependency(instance_of=int)

    ## ---------------------------- Other modules ports ----------------------------
    user_reader = providers.Factory(get_user_reader_impl)
    organization_member_reader = providers.Factory(
        get_organization_member_reader, session=session
    )
    member_role_reader = providers.Factory(get_member_role_reader, session=session)
    organization_membership_writer = providers.Factory(
        get_organization_membership_writer, session=session
    )
    organization_reader = providers.Factory(get_organization_reader, session=session)
    user_provisioner = providers.Factory(get_user_provisioner, session=session)

    ## ---------------------------- Infrastructure services ----------------------------

    ## ---------------------------- Repositories ----------------------------
    role_repository = providers.Factory(
        RoleRepositoryImpl, session=session, organization_id=organization_id
    )
    member_role_repository = providers.Factory(
        MemberRoleRepositoryImpl, session=session
    )
    permission_repository = providers.Factory(
        PermissionRepositoryImpl, session=session, organization_id=organization_id
    )
    team_repository = providers.Factory(
        TeamRepositoryImpl, session=session, organization_id=organization_id
    )
    team_member_repository = providers.Factory(
        TeamMemberRepositoryImpl, session=session
    )
    invitation_repository = providers.Factory(
        InvitationRepositoryImpl,
        session=session,
        organization_id=organization_id,
    )

    ## ---------------------------- Domain services ----------------------------

    rbac_role_domain_service = providers.Factory(
        RbacRoleDomainService, repository=role_repository
    )
    rbac_member_role_domain_service = providers.Factory(
        RbacMemberRoleDomainService, repository=member_role_repository
    )
    rbac_permission_domain_service = providers.Factory(
        RbacPermissionDomainService, repository=permission_repository
    )
    team_domain_service = providers.Factory(
        TeamDomainService, repository=team_repository
    )
    team_member_domain_service = providers.Factory(
        TeamMemberDomainService, repository=team_member_repository
    )
    invitation_token_service = providers.Factory(get_invitation_token_service)
    invitation_domain_service = providers.Factory(
        InvitationDomainService,
        repository=invitation_repository,
        token_service=invitation_token_service,
    )

    ## ---------------------------- Use cases ----------------------------
    create_role_usecase = providers.Factory(
        CreateRoleUseCase, rbac_role_domain_service=rbac_role_domain_service
    )

    list_roles_usecase = providers.Factory(
        ListRolesUseCase,
        rbac_role_domain_service=rbac_role_domain_service,
        user_reader=user_reader,
    )
    list_permissions_usecase = providers.Factory(
        ListPermissionsUseCase,
        rbac_permission_domain_service=rbac_permission_domain_service,
        user_reader=user_reader,
    )

    ## Team use cases
    create_team_usecase = providers.Factory(
        CreateTeamUseCase,
        team_domain_service=team_domain_service,
        team_member_domain_service=team_member_domain_service,
        organization_member_reader=organization_member_reader,
        organization_id=organization_id,
    )
    list_teams_usecase = providers.Factory(
        ListTeamsUseCase,
        team_domain_service=team_domain_service,
        team_member_domain_service=team_member_domain_service,
        organization_member_reader=organization_member_reader,
        user_reader=user_reader,
    )
    get_team_usecase = providers.Factory(
        GetTeamUseCase,
        team_domain_service=team_domain_service,
        user_reader=user_reader,
    )
    update_team_usecase = providers.Factory(
        UpdateTeamUseCase, team_domain_service=team_domain_service
    )
    delete_team_usecase = providers.Factory(
        DeleteTeamUseCase,
        team_domain_service=team_domain_service,
        team_member_domain_service=team_member_domain_service,
    )
    add_team_members_usecase = providers.Factory(
        AddTeamMembersUseCase,
        team_domain_service=team_domain_service,
        team_member_domain_service=team_member_domain_service,
        organization_member_reader=organization_member_reader,
        user_reader=user_reader,
        organization_id=organization_id,
    )
    list_team_members_usecase = providers.Factory(
        ListTeamMembersUseCase,
        team_domain_service=team_domain_service,
        team_member_domain_service=team_member_domain_service,
        organization_member_reader=organization_member_reader,
        user_reader=user_reader,
    )
    remove_team_member_usecase = providers.Factory(
        RemoveTeamMemberUseCase,
        team_domain_service=team_domain_service,
        team_member_domain_service=team_member_domain_service,
        organization_member_reader=organization_member_reader,
        member_role_reader=member_role_reader,
        organization_id=organization_id,
    )
    set_team_member_role_usecase = providers.Factory(
        SetTeamMemberRoleUseCase,
        team_domain_service=team_domain_service,
        team_member_domain_service=team_member_domain_service,
        organization_member_reader=organization_member_reader,
        organization_id=organization_id,
    )
    relocate_team_members_usecase = providers.Factory(
        RelocateTeamMembersUseCase,
        team_domain_service=team_domain_service,
        team_member_domain_service=team_member_domain_service,
        organization_member_reader=organization_member_reader,
        organization_id=organization_id,
    )

    ## Invitation use cases
    create_invitation_usecase = providers.Factory(
        CreateInvitationUseCase,
        invitation_domain_service=invitation_domain_service,
        rbac_role_domain_service=rbac_role_domain_service,
        team_domain_service=team_domain_service,
    )
    list_invitations_usecase = providers.Factory(
        ListInvitationsUseCase,
        invitation_domain_service=invitation_domain_service,
        user_reader=user_reader,
    )
    get_invitation_by_token_usecase = providers.Factory(
        GetInvitationByTokenUseCase,
        invitation_domain_service=invitation_domain_service,
        organization_reader=organization_reader,
        rbac_role_domain_service=rbac_role_domain_service,
    )
    accept_invitation_usecase = providers.Factory(
        AcceptInvitationUseCase,
        invitation_domain_service=invitation_domain_service,
        organization_membership_writer=organization_membership_writer,
        rbac_member_role_domain_service=rbac_member_role_domain_service,
        team_member_domain_service=team_member_domain_service,
    )
    revoke_invitation_usecase = providers.Factory(
        RevokeInvitationUseCase,
        invitation_domain_service=invitation_domain_service,
    )
    resend_invitation_usecase = providers.Factory(
        ResendInvitationUseCase,
        invitation_domain_service=invitation_domain_service,
    )
    signup_and_accept_invitation_usecase = providers.Factory(
        SignupAndAcceptInvitationUseCase,
        invitation_domain_service=invitation_domain_service,
        user_provisioner=user_provisioner,
        organization_membership_writer=organization_membership_writer,
        rbac_member_role_domain_service=rbac_member_role_domain_service,
        team_member_domain_service=team_member_domain_service,
    )


def get_workforce_container(
    session: AsyncSession, organization_id: int
) -> WorkforceContainer:
    """
    Factory function to create an instance of WorkforceContainer with the given session and organization_id.
    """
    container = WorkforceContainer()
    container.session.override(session)
    container.organization_id.override(organization_id)
    return container


def get_workforce_container_for_invitation_resolution(
    session: AsyncSession,
) -> WorkforceContainer:
    """
    Org-less bootstrap container for endpoints that resolve an invitation by
    raw token BEFORE the organization is known (public preview + the first
    step of the accept flow).

    Only the following providers are safe to use from this container:
      - invitation_domain_service.get_by_raw_token (token lookup is not
        organization-scoped — the hashed-token lookup ignores org_id)
      - organization_reader (organization-id agnostic)

    Calling org-scoped methods (filter/get_by/add/update) through this
    container WILL silently scope queries to organization_id=0 and return
    empty results — do not use it for those.
    """
    container = WorkforceContainer()
    container.session.override(session)
    container.organization_id.override(0)
    return container
