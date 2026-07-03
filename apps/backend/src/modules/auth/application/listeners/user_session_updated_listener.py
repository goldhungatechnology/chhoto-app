from src.modules.auth.domain.events.auth_session_domain_events import (
    UserSessionUpdatedEvent,
)
from src.shared.mediator.listener import listener


@listener(UserSessionUpdatedEvent)
async def on_user_session_updated(event: UserSessionUpdatedEvent):
    """
    remove the cache when a user session is updated, so that the next time the user sessio is requested, it will be fetched from the database and the cache will be updated with the new value.
    """
    from src.modules.auth.infrastructure.cache.auth_cache_service import (
        AuthCacheService,
    )

    auth_cache_service: AuthCacheService = AuthCacheService()

    return await auth_cache_service.delete_user_session(event.session_uuid)
