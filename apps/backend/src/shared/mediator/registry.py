import inspect
from collections import defaultdict
from dataclasses import dataclass, field

from src.shared.infrastructure.logger import logger


@dataclass
class HandlerInfo:
    """
    A dataclass to store the handler information for inspection and logging purposes
    """

    name: str
    module: str
    doc: str | None


@dataclass
class ListenerRegistry:
    """
    A registry to keep track of all the listeners registered in the system for inspection and logging purposes
    """

    _map: dict[str, list[HandlerInfo]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def record(self, event_type: type, handler) -> None:
        """
        record the handler information for the given event type in the registry
        """
        key = event_type.__name__
        self._map[key].append(
            HandlerInfo(
                name=handler.__name__,
                module=handler.__module__,
                doc=(inspect.getdoc(handler) or "").strip() or None,
            )
        )

    def inspect(self, event_type: type | None = None) -> dict[str, list[HandlerInfo]]:
        """
        inspect the registry and return the handlers for the given event type or all handlers if no event type is provided
        """
        if event_type is not None:
            key = event_type.__name__
            return {key: self._map.get(key, [])}
        return dict(self._map)

    def log_all(self) -> None:
        """
        log all the registered listeners in the registry for debugging and monitoring purposes
        """
        if not self._map:
            logger.info("[ListenerRegistry] No listeners registered.")
            return
        for event_name, handlers in self._map.items():
            names = ", ".join(h.name for h in handlers)
            logger.info("[ListenerRegistry] %s → [%s]", event_name, names)


registry = ListenerRegistry()
