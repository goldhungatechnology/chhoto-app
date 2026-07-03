from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class IBackplane(ABC):
    """
    An interface for a backplane that allows multiple instances of the gateway to communicate with each other. The backplane is responsible for publishing messages to channels and subscribing to channels to receive messages. The backplane should be implemented using a message broker such as Redis, RabbitMQ, or Kafka.
    """

    @abstractmethod
    async def publish(self, channel: str, message: dict) -> None:
        """
        Publish a message to a channel.
        """

    @abstractmethod
    def subscribe(self, patterns: list[str]) -> AsyncIterator[tuple[str, dict]]:
        """
        Subscribe to channels matching the given patterns and yield messages as they arrive. The method should return an asynchronous iterator that yields tuples of (channel, message) for each received message. The backplane should ensure that messages published by the same instance are not received by that instance to avoid processing its own messages.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """
        Close the backplane and release any resources. This method should be called when the gateway is shutting down to ensure that all connections to the message broker are properly closed.
        """
