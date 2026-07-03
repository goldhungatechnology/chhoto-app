from abc import ABC, abstractmethod


class IWebSocketService(ABC):
    @abstractmethod
    async def disconnect_agent_ws(self, sid: str) -> None:
        pass
