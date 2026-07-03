from enum import StrEnum


class GatewayEvent(StrEnum):
    VISITORS_SUBSCRIBE = "visitors.subscribe"
    VISITORS_SUBSCRIBE_ERROR = "visitors.subscribe.error"
    VISITORS_SUBSCRIBED = "visitors.subscribed"
    VISITORS_UNSUBSCRIBE = "visitors.unsubscribe"
    VISITORS_UNSUBSCRIBE_ERROR = "visitors.unsubscribe.error"
    VISITORS_UNSUBSCRIBED = "visitors.unsubscribed"

    VISITORS_ADDED = "visitors_added"
    VISITORS_UPDATED = "visitors_updated"
    VISITORS_REMOVED = "visitors_removed"
