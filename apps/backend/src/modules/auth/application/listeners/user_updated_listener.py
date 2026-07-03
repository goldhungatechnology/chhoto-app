from src.modules.auth.domain.events.auth_domain_events import UserUpdatedEvent
from src.shared.mediator.listener import listener


@listener(UserUpdatedEvent)
async def on_user_updated(event: UserUpdatedEvent):
    """
    remove the cache when a user is updated, so that the next time the user is requested, it will be fetched from the database and the cache will be updated with the new value.
    """
    from src.modules.auth.infrastructure.cache.auth_cache_service import (
        AuthCacheService,
    )

    auth_cache_service: AuthCacheService = AuthCacheService()

    return await auth_cache_service.delete_user_cache(event.user_id)


__all__ = ["on_user_updated"]
