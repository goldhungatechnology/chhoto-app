from typing import Literal

from .adapter.email.email_notification import (
    EmailNotification,
)
from .adapter.email.email_notification import (
    EmailNotificationMessage as EmailNotificationMessage,
)
from .interface.notification_interface import INotification


class NotificationFactory:
    """
    factory for notifications
    """

    _providers: dict[str, INotification] = {
        "email": EmailNotification(),
    }

    @classmethod
    def create(cls, n_type: Literal["email"]) -> INotification:
        """
        create notification instance based on type
        """
        provider = cls._providers.get(n_type)
        if provider is None:
            raise ValueError(f"Unsupported notification type: {n_type}")
        return provider
