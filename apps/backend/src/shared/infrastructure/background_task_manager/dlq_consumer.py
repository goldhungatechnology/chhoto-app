"""
DLQ (Dead Letter Queue) Consumer for handling failed background tasks.

This module provides utilities to consume and process messages from the DLQ
after they have exceeded max retries.
"""

from src.shared.infrastructure.logger import logger


class DLQConsumer:
    """
    Consumer for Dead Letter Queue messages.
    Provides methods to monitor and handle messages that failed after max retries.
    """

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.dlq_queue_name = "dlq"
        self.dlq_storage_key = "dlq_messages"

    def process_dlq_message(self, message: dict) -> None:
        """
        Process a message from the DLQ.
        Logs the failure details for monitoring/alerting.

        Args:
            message: The failed message from DLQ
        """
        message_id = message.get("message_id", "unknown")
        actor_name = message.get("actor_name", "unknown")
        retry_count = message.get("options", {}).get("max_retries", 0)
        error = message.get("error", "unknown error")

        logger.error(
            f"[DLQ-Consumer] Message moved to DLQ: "
            f"task={actor_name} message_id={message_id} "
            f"max_retries={retry_count} error={error}"
        )

        # Store in Redis for later inspection if needed
        self.store_dlq_message(message)

    def store_dlq_message(self, message: dict) -> None:
        """
        Store DLQ message in Redis for later inspection/alerting.

        Args:
            message: The failed message
        """
        try:
            import json
            from datetime import datetime

            message_id = message.get("message_id", "unknown")
            timestamp = datetime.utcnow().isoformat()

            dlq_entry = {
                "message_id": message_id,
                "timestamp": timestamp,
                "actor_name": message.get("actor_name"),
                "error": message.get("error"),
                "max_retries": message.get("options", {}).get("max_retries", 0),
                "message": message,
            }

            # Store with TTL (30 days)
            self.redis_client.setex(
                f"{self.dlq_storage_key}:{message_id}",
                30 * 24 * 60 * 60,
                json.dumps(dlq_entry, default=str),
            )

            logger.info(
                f"[DLQ-Consumer] Stored DLQ message for inspection: message_id={message_id}"
            )
        except Exception as e:
            logger.error(f"[DLQ-Consumer] Failed to store DLQ message: {e!s}")

    def get_dlq_messages(self, limit: int = 100) -> list[dict]:
        """
        Retrieve recent DLQ messages for monitoring/alerting.

        Args:
            limit: Maximum number of messages to retrieve

        Returns:
            List of DLQ message entries
        """
        try:
            import json

            keys = self.redis_client.keys(f"{self.dlq_storage_key}:*")
            messages = []

            for key in keys[:limit]:
                data = self.redis_client.get(key)
                if data:
                    messages.append(json.loads(data))

            return sorted(messages, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            logger.error(f"[DLQ-Consumer] Failed to retrieve DLQ messages: {e!s}")
            return []
