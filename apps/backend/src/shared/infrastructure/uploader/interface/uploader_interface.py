from abc import ABC, abstractmethod
from typing import Any


class UploaderInterface(ABC):
    """Interface for uploader adapters."""

    @abstractmethod
    async def upload_files(
        self, files: list[tuple[str, bytes, str | None]]
    ) -> list[dict[str, Any]]:
        """Upload files and return metadata including URL."""
        raise NotImplementedError
