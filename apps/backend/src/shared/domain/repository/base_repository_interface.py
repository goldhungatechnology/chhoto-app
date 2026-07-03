from abc import ABC, abstractmethod
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.entity.base_entity import BaseEntity

TEntity = TypeVar("TEntity", bound=BaseEntity)


class IBaseRepository[TEntity](ABC):
    """
    Generic async repository with explicit mapping between
    domain entity and ORM model.
    """

    def __init__(self, session: AsyncSession):
        """Initialize with an async database session."""
        self.session = session

    @abstractmethod
    async def add(
        self,
        entity: TEntity,
        *,
        audit: bool = True,
    ) -> TEntity:
        """Add a new entity to the repository."""

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> TEntity | None:
        """Find an entity by its ID."""

    @abstractmethod
    async def get_by_uuid(self, entity_uuid: str) -> TEntity | None:
        """Find an entity by its UUID."""

    @abstractmethod
    async def get_by(self, **criteria) -> TEntity | None:
        """
        get a single entity by arbitrary criteria
        """

    @abstractmethod
    async def update(
        self,
        entity: TEntity,
        *,
        audit: bool = True,
    ) -> TEntity:
        """Update an existing entity in the repository."""

    @abstractmethod
    async def delete(
        self,
        entity_id: int,
        audit: bool = True,
    ) -> None:
        """Delete an entity from the repository."""

    @abstractmethod
    async def filter(self, **criteria) -> list[TEntity]:
        """
        filter entities by arbitrary criteria
        """
