from src.shared.mediator.mediator import mediator
from src.shared.mediator.registry import registry


def listener(event_type):
    """
    a decroator for listening to an event, the function will be called when the event is emitted
    """

    def wrapper(func):
        mediator.register(event_type, func)
        registry.record(event_type, func)
        return func

    return wrapper
