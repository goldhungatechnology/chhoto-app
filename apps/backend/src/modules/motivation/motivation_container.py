from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.motivation.application.usecases.add_motivation_color_usecase import (
    AddMotivationColorUseCase,
)
from src.modules.motivation.application.usecases.create_motivation_quote_usecase import (
    CreateMotivationQuoteUseCase,
)
from src.modules.motivation.application.usecases.delete_motivation_quote_usecase import (
    DeleteMotivationQuoteUseCase,
)
from src.modules.motivation.application.usecases.get_daily_motivation_config_usecase import (
    GetDailyMotivationConfigUseCase,
)
from src.modules.motivation.application.usecases.get_daily_motivation_quote_usecase import (
    GetDailyMotivationQuoteUseCase,
)
from src.modules.motivation.application.usecases.get_motivation_quote_detail_usecase import (
    GetMotivationQuoteDetailUseCase,
)
from src.modules.motivation.application.usecases.get_motivation_quote_preview_slider_usecase import (
    GetMotivationQuotePreviewSliderUseCase,
)

from src.modules.motivation.application.usecases.list_motivation_colors_usecase import (
    ListMotivationColorsUseCase,
)
from src.modules.motivation.application.usecases.list_motivation_quotes_usecase import (
    ListMotivationQuotesUseCase,
)
from src.modules.motivation.application.usecases.list_system_motivation_quotes_usecase import (
    ListSystemMotivationQuotesUseCase,
)
from src.modules.motivation.application.usecases.react_to_motivation_quote_usecase import (
    ReactToMotivationQuoteUseCase,
)
from src.modules.motivation.application.usecases.update_daily_motivation_config_usecase import (
    UpdateDailyMotivationConfigUseCase,
)
from src.modules.motivation.application.usecases.update_motivation_quote_usecase import (
    UpdateMotivationQuoteUseCase,
)
from src.modules.motivation.domain.services.daily_motivation_config_domain_service import (
    DailyMotivationConfigDomainService,
)
from src.modules.motivation.domain.services.motivation_color_domain_service import (
    MotivationColorDomainService,
)
from src.modules.motivation.domain.services.motivation_quote_domain_service import (
    MotivationQuoteDomainService,
)
from src.modules.motivation.domain.services.motivation_quote_reaction_domain_service import (
    MotivationQuoteReactionDomainService,
)
from src.modules.motivation.infrastructure.repositories.daily_motivation_config_repository_impl import (
    DailyMotivationConfigRepositoryImpl,
)
from src.modules.motivation.infrastructure.repositories.motivation_color_repository_impl import (
    MotivationColorRepositoryImpl,
)
from src.modules.motivation.infrastructure.repositories.motivation_quote_reaction_repository_impl import (
    MotivationQuoteReactionRepositoryImpl,
)
from src.modules.motivation.infrastructure.repositories.motivation_quote_repository_impl import (
    MotivationQuoteRepositoryImpl,
)


class MotivationContainer(containers.DeclarativeContainer):
    """
    Container for motivation-related dependencies.
    """

    config = providers.Configuration()
    session = providers.Dependency(instance_of=AsyncSession)

    ## ------------------------ Repositories ------------------------ ##

    daily_motivation_config_repository = providers.Factory(
        DailyMotivationConfigRepositoryImpl,
        session=session,
    )

    motivation_quote_repository = providers.Factory(
        MotivationQuoteRepositoryImpl,
        session=session,
    )

    motivation_quote_reaction_repository = providers.Factory(
        MotivationQuoteReactionRepositoryImpl,
        session=session,
    )

    motivation_color_repository = providers.Factory(
        MotivationColorRepositoryImpl,
        session=session,
    )

    ## ------------------------ Domain Services ------------------------ ##

    daily_motivation_config_domain_service = providers.Factory(
        DailyMotivationConfigDomainService,
        repository=daily_motivation_config_repository,
    )

    motivation_quote_domain_service = providers.Factory(
        MotivationQuoteDomainService,
        quote_repository=motivation_quote_repository,
        config_repository=daily_motivation_config_repository,
    )

    motivation_quote_reaction_domain_service = providers.Factory(
        MotivationQuoteReactionDomainService,
        reaction_repository=motivation_quote_reaction_repository,
        quote_repository=motivation_quote_repository,
        config_repository=daily_motivation_config_repository,
    )

    motivation_color_domain_service = providers.Factory(
        MotivationColorDomainService,
        repository=motivation_color_repository,
    )

    ## ------------------------ Use Cases ------------------------ ##

    get_daily_motivation_config_usecase = providers.Factory(
        GetDailyMotivationConfigUseCase,
        daily_motivation_config_domain_service=daily_motivation_config_domain_service,
    )

    update_daily_motivation_config_usecase = providers.Factory(
        UpdateDailyMotivationConfigUseCase,
        daily_motivation_config_domain_service=daily_motivation_config_domain_service,
    )

    create_motivation_quote_usecase = providers.Factory(
        CreateMotivationQuoteUseCase,
        motivation_quote_domain_service=motivation_quote_domain_service,
    )

    list_motivation_quotes_usecase = providers.Factory(
        ListMotivationQuotesUseCase,
        motivation_quote_domain_service=motivation_quote_domain_service,
    )

    get_motivation_quote_detail_usecase = providers.Factory(
        GetMotivationQuoteDetailUseCase,
        motivation_quote_domain_service=motivation_quote_domain_service,
    )

    update_motivation_quote_usecase = providers.Factory(
        UpdateMotivationQuoteUseCase,
        motivation_quote_domain_service=motivation_quote_domain_service,
    )

    delete_motivation_quote_usecase = providers.Factory(
        DeleteMotivationQuoteUseCase,
        motivation_quote_domain_service=motivation_quote_domain_service,
    )

    get_daily_motivation_quote_usecase = providers.Factory(
        GetDailyMotivationQuoteUseCase,
        motivation_quote_domain_service=motivation_quote_domain_service,
    )

    get_motivation_quote_preview_slider_usecase = providers.Factory(
        GetMotivationQuotePreviewSliderUseCase,
        motivation_quote_domain_service=motivation_quote_domain_service,
    )

    list_system_motivation_quotes_usecase = providers.Factory(
        ListSystemMotivationQuotesUseCase,
        motivation_quote_domain_service=motivation_quote_domain_service,
    )

    react_to_motivation_quote_usecase = providers.Factory(
        ReactToMotivationQuoteUseCase,
        motivation_quote_reaction_domain_service=motivation_quote_reaction_domain_service,
    )

    list_motivation_colors_usecase = providers.Factory(
        ListMotivationColorsUseCase,
        config_domain_service=daily_motivation_config_domain_service,
        color_domain_service=motivation_color_domain_service,
    )

    add_motivation_color_usecase = providers.Factory(
        AddMotivationColorUseCase,
        config_domain_service=daily_motivation_config_domain_service,
        color_domain_service=motivation_color_domain_service,
    )


def get_motivation_container(session: AsyncSession) -> MotivationContainer:
    """
    Dependency injector for Motivation Container.
    """
    motivation_container = MotivationContainer()
    motivation_container.session.override(session)
    return motivation_container
