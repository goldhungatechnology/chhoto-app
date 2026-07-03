from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.application.usecases.login_usecase import LoginUseCase
from src.modules.auth.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)


class AuthContainer(containers.DeclarativeContainer):
    """
    Container for authentication-related dependencies.
    TODO: Add configuration mapping and other usecase/repository injections here.
    """

    config = providers.Configuration()

    session = providers.Dependency(instance_of=AsyncSession)

    # Repositories
    user_repository = providers.Factory(UserRepositoryImpl, session=session)

    # Use Cases
    login_usecase = providers.Factory(
        LoginUseCase,
        user_repository=user_repository,
    )


def get_auth_container(session: AsyncSession) -> AuthContainer:
    """
    Utility factory to build and inject the AuthContainer with the active session.
    """
    container = AuthContainer()
    container.session.override(session)
    return container
