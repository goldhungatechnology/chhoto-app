# shared/infrastructure/outbox/registry.py

from collections.abc import Callable

handlers: dict[str, Callable] = {}


def outbox_handler(event_type: str):
    """
    a decorator to register a handler for a specific event type, the handler will be called by the outbox processor when it processes an event of that type.
    """

    def wrapper(func: Callable):
        handlers[event_type] = func
        return func

    return wrapper
