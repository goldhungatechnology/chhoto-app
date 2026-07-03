import json
from datetime import UTC, datetime
from typing import Any, Protocol, cast

from dramatiq.middleware.asyncio import AsyncIO

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Middleware

from src.core.config.settings import config
from src.shared.infrastructure.background_task_manager.interface.background_task_manager_interface import (
    BackgroundTaskManagerInterface,
    TaskInterface,
)
from src.shared.infrastructure.logger import logger


class RedisDLQClientProtocol(Protocol):
    """Minimal Redis client interface for DLQ storage."""

    def setex(self, key: str, ttl: int, value: str) -> Any: ...
    def lpush(self, key: str, value: str) -> Any: ...
    def ltrim(self, key: str, start: int, end: int) -> Any: ...
    def expire(self, key: str, ttl: int) -> Any: ...


class RetryLoggingMiddleware(Middleware):
    """Logs retry attempts for background tasks."""

    def before_nack(self, broker: Any, message: Any) -> None:
        """Log retry attempt before message is re-queued."""
        retry_count = message.options.get("retries", 0)
        max_retries = message.options.get("max_retries", 0)

        if max_retries > 0:
            logger.warning(
                f"[Background-Task] task={message.actor_name} "
                f"message_id={message.message_id} "
                f"attempt={retry_count + 1}/{max_retries + 1}"
            )


class DLQMiddleware(Middleware):
    """Stores failed messages in Redis DLQ after max retries."""

    def __init__(self):
        """Initialize DLQ keys."""
        self.dlq_key_prefix = "dlq_message"
        self.dlq_list_key = "dlq_messages_list"

    def after_nack(self, broker: Any, message: Any) -> None:
        """Store message in DLQ if retries are exhausted."""
        retry_count = message.options.get("retries", 0)
        max_retries = message.options.get("max_retries", 0)

        if max_retries > 0 and retry_count >= max_retries:
            self._store_to_dlq(broker, message)

    def _store_to_dlq(self, broker: Any, message: Any) -> None:
        """Persist failed message in Redis DLQ."""
        try:
            redis_client = getattr(broker, "client", None)
            if not redis_client:
                return

            entry = {
                "message_id": message.message_id,
                "task_name": message.actor_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "options": message.options,
                "args": str(message.args),
                "kwargs": str(message.kwargs),
            }

            key = f"{self.dlq_key_prefix}:{message.message_id}"

            redis_client.setex(key, 604800, json.dumps(entry, default=str))
            redis_client.lpush(self.dlq_list_key, json.dumps(entry, default=str))
            redis_client.ltrim(self.dlq_list_key, 0, 999)
            redis_client.expire(self.dlq_list_key, 604800)

        except Exception as e:
            logger.error(f"[DLQ] store failed: {e!s}")


# Redis broker setup
broker = RedisBroker(url=config.REDIS_URL)
broker.add_middleware(RetryLoggingMiddleware())
broker.add_middleware(DLQMiddleware())
broker.add_middleware(AsyncIO())

dramatiq.set_broker(broker)


class DramatiqTask(TaskInterface):
    """Wrapper around Dramatiq actor for task execution."""

    def __init__(self, func, queue_name: str):
        """Create a Dramatiq actor from a function."""
        self.func = func
        self.func_name = func.__name__

        actor_factory = cast(Any, dramatiq.actor)

        self.dramatiq_actor = actor_factory(
            func,
            queue_name=queue_name,
        )

    def queue(self, *args, **kwargs):
        """Queue task for execution."""
        logger.success(f"[Background-Task] queued -> {self.func_name}")
        return self.dramatiq_actor.send(*args, **kwargs)

    def queue_with_options(self, task_options: dict | None = None, *args, **kwargs):
        """Queue task with additional execution options."""
        logger.success(f"[Background-Task] queued (opts) -> {self.func_name}")
        return self.dramatiq_actor.send_with_options(
            args=args,
            kwargs=kwargs,
            **(task_options or {}),
        )


class DramatiqBackgroundTaskManager(BackgroundTaskManagerInterface):
    """Background task manager using Dramatiq."""

    def add_task(self, task_callable) -> DramatiqTask:
        """Register a new background task."""
        return DramatiqTask(task_callable, queue_name=task_callable.__name__)

    def list_tasks(self):
        """List registered tasks (not implemented)."""
        pass
