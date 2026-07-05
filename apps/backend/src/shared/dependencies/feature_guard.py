from enum import StrEnum
from functools import wraps
from typing import Any, Awaitable, Callable

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.db import get_async_session


def require_feature(feature_key: str | StrEnum, amount: int = 1):
    """
    Stub dependency to always allow feature usage.
    """

    async def dependency(
        request: Request,
        session: AsyncSession = Depends(get_async_session),
    ):
        return {"allowed": True, "reason": None}

    return dependency


def require_feature_decorator(feature_key: str | StrEnum, amount: int = 1):
    """
    Stub decorator to always allow feature usage.
    """

    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
