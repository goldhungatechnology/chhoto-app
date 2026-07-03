from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.billing.domain.services.billing_plan_limit_domain_service import (
    BillingPlanLimitDomainService,
)
from src.modules.billing.domain.services.billing_subscription_domain_service import (
    BillingSubscriptionDomainService,
)
from src.modules.billing.domain.services.entitlement_domain_service import (
    EntitlementDomainService,
)
from src.modules.billing.domain.services.organization_feature_usage_domain_service import (
    OrganizationFeatureUsageDomainService,
)
from src.modules.billing.infrastructure.repositories.billing_plan_limit_repository_impl import (
    BillingPlanLimitRepositoryImpl,
)
from src.modules.billing.infrastructure.repositories.billing_subscription_repository_impl import (
    BillingSubscriptionRepositoryImpl,
)
from src.modules.billing.infrastructure.repositories.organization_feature_usage_repository_impl import (
    OrganizationFeatureUsageRepositoryImpl,
)
from src.modules.billing.application.usecases.increment_feature_usage_usecase import (
    IncrementFeatureUsageUseCase,
)


class BillingContainer(containers.DeclarativeContainer):
    session = providers.Dependency(instance_of=AsyncSession)
    organization_id = providers.Dependency(instance_of=int)

    billing_subscription_repository = providers.Factory(
        BillingSubscriptionRepositoryImpl,
        session=session,
        organization_id=organization_id,
    )

    billing_plan_limit_repository = providers.Factory(
        BillingPlanLimitRepositoryImpl,
        session=session,
    )

    organization_feature_usage_repository = providers.Factory(
        OrganizationFeatureUsageRepositoryImpl,
        session=session,
        organization_id=organization_id,
    )

    billing_subscription_domain_service = providers.Factory(
        BillingSubscriptionDomainService,
        repository=billing_subscription_repository,
    )

    billing_plan_limit_domain_service = providers.Factory(
        BillingPlanLimitDomainService,
        repository=billing_plan_limit_repository,
    )

    organization_feature_usage_domain_service = providers.Factory(
        OrganizationFeatureUsageDomainService,
        repository=organization_feature_usage_repository,
    )

    entitlement_domain_service = providers.Factory(
        EntitlementDomainService,
        subscription_service=billing_subscription_domain_service,
        plan_limit_service=billing_plan_limit_domain_service,
        feature_usage_service=organization_feature_usage_domain_service,
    )

    increment_feature_usage_usecase = providers.Factory(
        IncrementFeatureUsageUseCase,
        subscription_service=billing_subscription_domain_service,
        feature_usage_service=organization_feature_usage_domain_service,
    )


def get_billing_container(
    session: AsyncSession,
    organization_id: int,
) -> BillingContainer:
    container = BillingContainer()
    container.session.override(session)
    container.organization_id.override(organization_id)
    return container
