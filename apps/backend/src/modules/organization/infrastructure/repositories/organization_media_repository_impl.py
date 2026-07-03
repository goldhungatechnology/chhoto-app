from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organization.domain.entities.organization_media_entity import (
    OrganizationMediaEntity,
)
from src.modules.organization.domain.repositories.organization_media_repository import (
    IOrganizationMediaRepository,
)
from src.modules.organization.infrastructure.models.organization_media_model import (
    OrganizationMediaModel,
)


class OrganizationMediaRepositoryImpl(IOrganizationMediaRepository):
    """
    SQLAlchemy repository implementation for organization media.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
        self,
        entity: OrganizationMediaEntity,
        *,
        audit: bool = True,
    ) -> OrganizationMediaEntity:
        model = OrganizationMediaModel(
            uuid=entity.uuid,
            organization_id=entity.organization_id,
            whatsapp=entity.whatsapp,
            linkedin=entity.linkedin,
            email=entity.email,
            phone_number=entity.phone_number,
            messenger=entity.messenger,
            instagram=entity.instagram,
            twitter=entity.twitter,
            telegram=entity.telegram,
            created_by_id=entity.created_by_id if audit else None,
            updated_by_id=entity.updated_by_id if audit else None,
        )

        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)

        return self._to_entity(model)

    async def get_by(self, **criteria) -> OrganizationMediaEntity | None:
        stmt = select(OrganizationMediaModel)

        for field_name, value in criteria.items():
            model_field = getattr(OrganizationMediaModel, field_name)
            stmt = stmt.where(model_field == value)

        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_entity(model)

    async def update(
        self,
        entity: OrganizationMediaEntity,
        *,
        audit: bool = True,
    ) -> OrganizationMediaEntity:
        model = await self.session.get(OrganizationMediaModel, entity.id)

        if not model:
            return entity

        model.whatsapp = entity.whatsapp
        model.linkedin = entity.linkedin
        model.email = entity.email
        model.phone_number = entity.phone_number
        model.messenger = entity.messenger
        model.instagram = entity.instagram
        model.twitter = entity.twitter
        model.telegram = entity.telegram
        model.updated_at = datetime.now(UTC)

        if audit:
            model.updated_by_id = entity.updated_by_id

        await self.session.flush()
        await self.session.refresh(model)

        return self._to_entity(model)

    def _to_entity(self, model: OrganizationMediaModel) -> OrganizationMediaEntity:
        return OrganizationMediaEntity(
            id=model.id,
            uuid=model.uuid,
            organization_id=model.organization_id,
            whatsapp=model.whatsapp,
            linkedin=model.linkedin,
            email=model.email,
            phone_number=model.phone_number,
            messenger=model.messenger,
            instagram=model.instagram,
            twitter=model.twitter,
            telegram=model.telegram,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by_id=model.created_by_id,
            updated_by_id=model.updated_by_id,
        )
