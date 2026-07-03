from src.modules.visitor.domain.entities.visitor_entity import VisitorEntity
from src.modules.visitor.domain.repositories.visitor_repository import (
    IVisitorRepository,
)
from src.shared.exceptions.base_exceptions import (
    ConflictError,
    DomainError,
    ServerError,
)


class VisitorDomainService:
    """
    Domain service encapsulating visitor identity rules (upsert / identify).
    """

    def __init__(self, repository: IVisitorRepository):
        self.repository = repository

    async def upsert_visitor(
        self,
        *,
        organization_id: int,
        external_id: str,
        name: str | None = None,
        email: str | None = None,
    ) -> VisitorEntity:
        """
        Resolve a visitor for ``(organization_id, external_id)``.

        - existing visitor -> bump visit count, refresh last-seen, apply any
          newly supplied identity, persist and return.
        - new visitor       -> create it.

        A concurrent first-visit race (two sessions starting at once) can make
        the insert collide on the per-organization uniqueness constraint; in
        that case we fall back to fetching and updating the row that won.
        """
        existing = await self.repository.get_by_external_id(
            organization_id, external_id
        )
        if existing:
            return await self._apply_return_visit(existing, name=name, email=email)

        visitor = VisitorEntity(
            organization_id=organization_id,
            external_id=external_id,
            name=name,
            email=email,
            is_identified=bool(name or email),
        )

        try:
            return await self.repository.add(visitor)
        except ConflictError:
            # Lost the create race — the other writer inserted first.
            winner = await self.repository.get_by_external_id(
                organization_id, external_id
            )
            if not winner:
                raise
            return await self._apply_return_visit(winner, name=name, email=email)

    async def get_by_id(self, visitor_id: int) -> VisitorEntity | None:
        """Fetch a visitor by internal id."""
        return await self.repository.get_by_id(visitor_id)

    async def _apply_return_visit(
        self,
        visitor: VisitorEntity,
        *,
        name: str | None,
        email: str | None,
    ) -> VisitorEntity:
        """Mutate + persist a returning visitor."""
        try:
            visitor.register_return_visit()
            if name or email:
                visitor.identify(name=name, email=email)
            return await self.repository.update(visitor)
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="Failed to update visitor", internal_details=str(e)
            ) from e
