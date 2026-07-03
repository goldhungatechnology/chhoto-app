"""
Background task monitoring routers.
Exposes endpoints to view DLQ (Dead Letter Queue) messages and retry statistics.
"""

import json
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.shared.infrastructure.background_task_manager.adapter.dramatiq.dramatiq_background_task_manager import (
    broker,
)
from src.shared.infrastructure.logger import logger

# -----------------------------
# Schemas
# -----------------------------


class DLQMessageSchema(BaseModel):
    message_id: str
    timestamp: str
    task_name: str | None = None
    max_retries: int = 0


class DLQListResponseSchema(BaseModel):
    items: list[DLQMessageSchema]
    total: int


# -----------------------------
# Router
# -----------------------------

router = APIRouter(
    prefix="/api/v1/background-tasks",
    tags=["background-tasks"],
)


# -----------------------------
# Redis Access Layer (FIXED)
# -----------------------------


def get_redis_client() -> Any | None:
    """
    Safe extraction of Redis client from Dramatiq broker.

    NOTE: Ideally this should be injected instead of introspected.
    """
    redis_client = getattr(broker, "client", None)

    if redis_client:
        return redis_client

    redis_func = getattr(broker, "_redis_client", None)

    if callable(redis_func):
        try:
            return redis_func()
        except Exception as e:
            logger.error(f"[DLQ] Failed to resolve Redis client: {e}")
            return None

    return redis_func


# -----------------------------
# DLQ Repository Layer
# -----------------------------

DLQ_LIST_KEY = "dlq_messages_list"
DLQ_DETAIL_PREFIX = "dlq_message:"


class DLQRepository:
    def __init__(self, redis):
        self.redis = redis

    def list_messages(self, start: int, end: int) -> list[dict]:
        raw = self.redis.lrange(DLQ_LIST_KEY, start, end)
        return [json.loads(x) for x in raw if x]

    def count(self) -> int:
        return self.redis.llen(DLQ_LIST_KEY)

    def get_message(self, message_id: str) -> dict | None:
        raw = self.redis.get(f"{DLQ_DETAIL_PREFIX}{message_id}")
        return json.loads(raw) if raw else None


# -----------------------------
# Endpoints
# -----------------------------


@router.get("/dlq", response_model=DLQListResponseSchema)
async def get_dlq_messages(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> DLQListResponseSchema:
    """
    List DLQ messages with pagination.
    """
    try:
        redis = get_redis_client()

        if not redis:
            logger.warning("[DLQ] Redis not available")
            return DLQListResponseSchema(items=[], total=0)

        repo = DLQRepository(redis)

        raw_messages = repo.list_messages(offset, offset + limit - 1)
        total = repo.count()

        items = [
            DLQMessageSchema(
                message_id=m.get("message_id", "unknown"),
                timestamp=m.get("timestamp", ""),
                task_name=m.get("task_name"),
                max_retries=m.get("max_retries", 0),
            )
            for m in raw_messages
        ]

        return DLQListResponseSchema(items=items, total=total)

    except Exception as e:
        logger.error(f"[DLQ] list error: {e}")
        return DLQListResponseSchema(items=[], total=0)


@router.get("/dlq/{message_id}")
async def get_dlq_message_detail(message_id: str):
    """
    Get a single DLQ message.
    """
    try:
        redis = get_redis_client()

        if not redis:
            return {"error": "Redis not available", "message_id": message_id}

        repo = DLQRepository(redis)
        msg = repo.get_message(message_id)

        if not msg:
            return {"error": "Message not found", "message_id": message_id}

        return {
            "message_id": msg.get("message_id"),
            "task_name": msg.get("task_name"),
            "timestamp": msg.get("timestamp"),
            "max_retries": msg.get("max_retries"),
            "args": msg.get("args"),
            "kwargs": msg.get("kwargs"),
        }

    except Exception as e:
        logger.error(f"[DLQ] detail error: {e}")
        return {"error": str(e), "message_id": message_id}
