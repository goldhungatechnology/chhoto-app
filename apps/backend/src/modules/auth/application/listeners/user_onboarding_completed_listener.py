from src.shared.mediator.listener import listener
from src.modules.auth.domain.events.auth_onboarding_domain_events import (
    UserOnboardingCompletedEvent,
)


@listener(UserOnboardingCompletedEvent)
async def on_user_boarding_completed(event: UserOnboardingCompletedEvent):
    """
    Invalidate user cache when onboarding is completed so the next request fetches the updated user.
    """
    from src.modules.auth.infrastructure.cache.auth_cache_service import (
        AuthCacheService,
    )

    auth_cache_service: AuthCacheService = AuthCacheService()
    return await auth_cache_service.delete_user_cache(event.user_id)


__all__ = ["on_user_boarding_completed"]
