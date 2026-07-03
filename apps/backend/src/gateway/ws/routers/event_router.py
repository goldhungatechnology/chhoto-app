from typing import Callable


class EventRouter:
    """
    A simple event router that allows registering handlers for different event types and dispatching events to the appropriate handlers. Handlers are registered using the `register` method, which takes an event type as an argument and returns a decorator. The `handle` method is used to dispatch events, which looks up the handler for the given event type and calls it with the user ID and event payload.
    """

    def __init__(self):
        self.handlers: dict[str, Callable] = {}

    def register(self, event_type: str):
        """
        A decorator for registering a handler for a specific event type. The decorated function should take two arguments: `user_id` (the ID of the user associated with the event) and `payload` (the data associated with the event). The handler is stored in the `handlers` dictionary, keyed by the event type.
        """

        def wrapper(func: Callable):
            self.handlers[event_type] = func
            return func

        return wrapper

    async def handle(self, user_id: int | None, event: dict):
        """
        Handle an incoming event by looking up the appropriate handler based on the event type and calling it with the user ID and event payload. If the event is missing the 'type' field or if there is no registered handler for the event type, an error message is returned.
        """
        event_type = event.get("type")
        if not event_type:
            return {"error": "Missing 'type' field in event"}

        handler = self.handlers.get(event_type)
        if not handler:
            return {"error": f"Unknown event: {event_type}"}

        payload = event.get("payload", {})
        return await handler(user_id, payload)


global_event_router = EventRouter()
