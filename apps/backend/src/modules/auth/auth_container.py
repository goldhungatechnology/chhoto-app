from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.usecases.core.edit_user_usecase import EditUserUseCase
from src.modules.auth.application.usecases.core.get_user_details_usecase import (
    GetUserDetailsUseCase,
)
from src.modules.auth.application.usecases.core.logout_user_usecase import (
    LogoutUserUseCase,
)
from src.modules.auth.application.usecases.email.email_verificiation_resend_usecase import (
    EmailVerificationResendUseCase,
)
from src.modules.auth.application.usecases.oauth.authenticate_user_oauth_usecase import (
    AuthenticatUserOAuthUseCase,
)
from src.modules.auth.application.usecases.oauth.begin_oauth_usecase import (
    BeginOAuthUseCase,
)
from src.modules.auth.application.usecases.interface_setup.interface_setup_usecase import (
    InterfaceSetupUseCase,
)
from src.modules.auth.application.usecases.onboarding.create_onboarding_usecase import (
    CreateOnboardingUseCase,
)
from src.modules.auth.application.usecases.password.forgot_password_usecase import (
    ForgotPasswordUseCase,
)
from src.modules.auth.application.usecases.password.reset_password_usecase import (
    ResetPasswordUseCase,
)
from src.modules.auth.application.usecases.password.verify_forgot_password_usecase import (
    VerifyForgotPasswordUseCase,
)
from src.modules.auth.application.usecases.session.get_user_session_usecase import (
    GetUserSessionUseCase,
)
from src.modules.auth.application.usecases.session.list_all_user_session_usecase import (
    ListAllUserSessionUseCase,
)
from src.modules.auth.application.usecases.session.revoke_all_user_sessions_usecase import (
    RevokeAllUserSessionsUseCase,
)
from src.modules.auth.application.usecases.session.revoke_user_session_usecase import (
    RevokeUserSessionUseCase,
)
from src.modules.auth.application.usecases.core.create_user_usecase import (
    CreateUserUseCase,
)
from src.modules.auth.application.usecases.mfa.confirm_mfa_usecase import (
    ConfirmMFAUseCase,
)
from src.modules.auth.application.usecases.mfa.disable_mfa_usecase import (
    DisableMFAUseCase,
)
from src.modules.auth.application.usecases.mfa.setup_mfa_usecase import (
    SetupMFAUseCase,
)
from src.modules.auth.application.usecases.mfa.verify_mfa_usecase import (
    VerifyMFAUseCase,
)
from src.modules.auth.application.usecases.core.login_user_usecase import (
    LoginUserUseCase,
)
from src.modules.auth.application.usecases.email.email_verification_usecase import (
    EmailVerificationUseCase,
)
from src.modules.auth.domain.services.user_account_domain_service import (
    UserAccountDomainService,
)
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_mfa_domain_service import (
    UserMFADomainService,
)
from src.modules.auth.domain.services.user_onboarding_domain_service import (
    UserOnboardingDomainService,
)
from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.modules.auth.domain.services.user_token_domain_service import (
    UserTokenDomainService,
)
from src.modules.auth.infrastructure.cache.auth_cache_service import AuthCacheService
from src.modules.auth.infrastructure.email_validator.email_validator_impl import (
    EmailDomainValidatorImpl,
)
from src.modules.auth.infrastructure.repositories.user_account_repository_impl import (
    UserAccountRepositoryImpl,
)
from src.modules.auth.infrastructure.repositories.user_mfa_repository_impl import (
    UserMFARepositoryImpl,
)
from src.modules.auth.infrastructure.repositories.user_onboarding_repository_impl import (
    UserOnboardingRepositoryImpl,
)
from src.modules.auth.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from src.modules.auth.infrastructure.repositories.user_session_repository_impl import (
    UserSessionRepositoryImpl,
)
from src.modules.auth.infrastructure.repositories.user_token_repository_impl import (
    UserTokenRepositoryImpl,
)
from src.shared.infrastructure.country.country_reader import get_country_reader
from src.shared.infrastructure.geoip.geoip_service import (
    geoip_service as geoip_service_singleton,
)
from src.shared.infrastructure.hasher.hasher import HasherService
from src.shared.infrastructure.token.token_service import TokenService
from src.modules.auth.infrastructure.totp.totp_service import TOTPService


class AuthContainer(containers.DeclarativeContainer):
    """
    Container for authentication-related dependencies.
    """

    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)

    country_reader = providers.Factory(get_country_reader, session=session)

    ## ---------------------------- Shared singletons ----------------------------
    # Process-wide GeoIP reader (loaded once during app lifespan).
    geoip_service = providers.Object(geoip_service_singleton)

    ## ---------------------------- Infrastructure services ----------------------------
    token_service = providers.Factory(TokenService)
    hasher_service = providers.Factory(
        HasherService
    )  # Placeholder for a hasher service implementation
    cache_service = providers.Factory(AuthCacheService)
    totp_service = providers.Factory(TOTPService)

    ## ---------------------------- Repositories ----------------------------
    user_repository = providers.Factory(UserRepositoryImpl, session=session)
    user_account_repository = providers.Factory(
        UserAccountRepositoryImpl, session=session
    )
    user_session_repository = providers.Factory(
        UserSessionRepositoryImpl, session=session
    )
    user_token_repository = providers.Factory(UserTokenRepositoryImpl, session=session)
    user_mfa_repository = providers.Factory(UserMFARepositoryImpl, session=session)
    user_onboarding_repository = providers.Factory(
        UserOnboardingRepositoryImpl, session=session
    )

    ## ---------------------------- Validators ----------------------------
    email_validator = providers.Factory(EmailDomainValidatorImpl)

    ## ---------------------------- Domain Services ----------------------------
    user_domain_service = providers.Factory(
        UserDomainService,
        repository=user_repository,
        email_validator=email_validator,
    )
    user_account_domain_service = providers.Factory(
        UserAccountDomainService,
        repository=user_account_repository,
    )
    user_session_domain_service = providers.Factory(
        UserSessionDomainService,
        repository=user_session_repository,
    )
    user_token_domain_service = providers.Factory(
        UserTokenDomainService,
        repository=user_token_repository,
        token_service=token_service,
        hasher=hasher_service,
    )
    user_mfa_domain_service = providers.Factory(
        UserMFADomainService,
        repository=user_mfa_repository,
    )
    user_onboarding_domain_service = providers.Factory(
        UserOnboardingDomainService,
        repository=user_onboarding_repository,
    )

    ## ---------------------------- Use Cases ----------------------------
    create_user_usecase = providers.Factory(
        CreateUserUseCase,
        user_domain_service=user_domain_service,
        user_account_domain_service=user_account_domain_service,
        user_session_domain_service=user_session_domain_service,
        user_token_domain_service=user_token_domain_service,
        hasher_service=hasher_service,
        geoip_service=geoip_service,
        country_reader=country_reader,
    )

    get_user_details_usecase = providers.Factory(
        GetUserDetailsUseCase,
        user_domain_service=user_domain_service,
        user_onboarding_domain_service=user_onboarding_domain_service,
        user_account_domain_service=user_account_domain_service,
        user_session_domain_service=user_session_domain_service,
        cache_service=cache_service,
        country_reader=country_reader,
        user_mfa_domain_service=user_mfa_domain_service,
    )

    edit_user_usecase = providers.Factory(
        EditUserUseCase,
        user_domain_service=user_domain_service,
        country_reader=country_reader,
    )

    email_verification_usecase = providers.Factory(
        EmailVerificationUseCase,
        user_domain_service=user_domain_service,
        user_token_domain_service=user_token_domain_service,
    )

    email_verification_resend_usecase = providers.Factory(
        EmailVerificationResendUseCase,
        user_domain_service=user_domain_service,
        user_token_domain_service=user_token_domain_service,
    )

    login_user_usecase = providers.Factory(
        LoginUserUseCase,
        user_domain_service=user_domain_service,
        user_session_domain_service=user_session_domain_service,
        user_mfa_domain_service=user_mfa_domain_service,
        user_account_domain_service=user_account_domain_service,
        hasher_service=hasher_service,
        token_service=token_service,
    )

    logout_user_usecase = providers.Factory(
        LogoutUserUseCase,
        user_session_domain_service=user_session_domain_service,
    )

    get_user_session_usecase = providers.Factory(
        GetUserSessionUseCase,
        user_session_domain_service=user_session_domain_service,
        cache_service=cache_service,
    )

    list_all_user_sessions_usecase = providers.Factory(
        ListAllUserSessionUseCase,
        user_session_domain_service=user_session_domain_service,
    )

    revoke_all_user_sessions_usecase = providers.Factory(
        RevokeAllUserSessionsUseCase,
        user_session_domain_service=user_session_domain_service,
        cache_service=cache_service,
    )

    revoke_user_session_usecase = providers.Factory(
        RevokeUserSessionUseCase,
        user_session_domain_service=user_session_domain_service,
        cache_service=cache_service,
    )

    create_onboarding_usecase = providers.Factory(
        CreateOnboardingUseCase,
        user_onboarding_domain_service=user_onboarding_domain_service,
        user_domain_service=user_domain_service,
    )

    interface_setup_usecase = providers.Factory(
        InterfaceSetupUseCase,
        user_onboarding_domain_service=user_onboarding_domain_service,
    )

    forgot_password_usecase = providers.Factory(
        ForgotPasswordUseCase,
        user_domain_service=user_domain_service,
        user_token_domain_service=user_token_domain_service,
    )

    reset_password_usecase = providers.Factory(
        ResetPasswordUseCase,
        user_account_domain_service=user_account_domain_service,
        revoke_all_user_sessions_usecase=revoke_all_user_sessions_usecase,
        hasher=hasher_service,
    )

    verify_forgot_password_usecase = providers.Factory(
        VerifyForgotPasswordUseCase,
        user_domain_service=user_domain_service,
        user_account_domain_service=user_account_domain_service,
        user_token_domain_service=user_token_domain_service,
        revoke_all_user_sessions_usecase=revoke_all_user_sessions_usecase,
        hasher=hasher_service,
    )

    begin_oauth_usecase = providers.Factory(
        BeginOAuthUseCase,
    )

    authenticate_user_oauth_usecase = providers.Factory(
        AuthenticatUserOAuthUseCase,
        user_domain_service=user_domain_service,
        user_account_domain_service=user_account_domain_service,
        user_mfa_domain_service=user_mfa_domain_service,
        user_session_domain_service=user_session_domain_service,
        token_service=token_service,
    )

    ## ---------------------------- MFA Use Cases ----------------------------
    setup_mfa_usecase = providers.Factory(
        SetupMFAUseCase,
        user_domain_service=user_domain_service,
        user_mfa_domain_service=user_mfa_domain_service,
        totp_service=totp_service,
    )

    confirm_mfa_usecase = providers.Factory(
        ConfirmMFAUseCase,
        user_mfa_domain_service=user_mfa_domain_service,
        totp_service=totp_service,
    )

    disable_mfa_usecase = providers.Factory(
        DisableMFAUseCase,
        user_mfa_domain_service=user_mfa_domain_service,
        user_account_domain_service=user_account_domain_service,
        hasher_service=hasher_service,
    )

    verify_mfa_usecase = providers.Factory(
        VerifyMFAUseCase,
        user_mfa_domain_service=user_mfa_domain_service,
        user_session_domain_service=user_session_domain_service,
        totp_service=totp_service,
        token_service=token_service,
    )


def get_auth_container(session: AsyncSession) -> AuthContainer:
    """
    Dependency injector for Auth Container
    """
    auth_container = AuthContainer()
    auth_container.session.override(session)
    return auth_container
