from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.modules.motivation.domain.repositories.motivation_quote_repository import (
    IMotivationQuoteRepository,
)
from src.modules.motivation.infrastructure.models.motivation_quote_model import (
    MotivationQuoteModel,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.base_repository import BaseRepository


class MotivationQuoteRepositoryImpl(
    BaseRepository[MotivationQuoteEntity], IMotivationQuoteRepository
):
    """
    SQLAlchemy implementation of the motivation quote repository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = MotivationQuoteModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: MotivationQuoteEntity) -> dict:
        """
        Convert MotivationQuoteEntity to database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "text": entity.context,
            "author_name": entity.author_name,
            "is_sys_default": entity.is_sys_default,
            "status": entity.status,
            "language_code": "en",
            "display_time": "09:00 AM",
            "text_style": entity.font_style,
            "theme_color": entity.theme_color,
            "bg_image": entity.bg_image,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "deleted_at": entity.deleted_at,
        }

    def to_entity(self, row: dict) -> MotivationQuoteEntity:
        """
        Convert database row to MotivationQuoteEntity.
        """
        return MotivationQuoteEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row.get("organization_id"),
            context=row["text"],
            author_name=row.get("author_name"),
            is_sys_default=row["is_sys_default"],
            status=row["status"],
            font_style=row["text_style"],
            theme_color=row["theme_color"],
            bg_image=row.get("bg_image"),
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row.get("deleted_at"),
        )

    async def list_by_organization_id(
        self,
        organization_id: int,
        is_sys_default: bool | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[MotivationQuoteEntity]:
        """
        List motivation quotes by organization id.
        """
        sql = f"""
            SELECT * FROM {self.table_name}
            WHERE organization_id = :organization_id
            AND deleted_at IS NULL
        """

        params: dict[str, object] = {
            "organization_id": organization_id,
        }

        if is_sys_default is not None:
            sql += " AND is_sys_default = :is_sys_default"
            params["is_sys_default"] = is_sys_default

        if status is not None:
            sql += " AND status = :status"
            params["status"] = status

        if search is not None:
            sql += " AND text ILIKE :search"
            params["search"] = f"%{search}%"

        sql += " ORDER BY created_at DESC"

        try:
            result = await self.session.execute(text(sql), params)
            rows = result.mappings().all()
            return [self.to_entity(dict(row)) for row in rows]
        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to list motivation quotes",
                internal_details=str(e),
            ) from e

    async def get_active_custom_quote(
        self,
        organization_id: int,
    ) -> MotivationQuoteEntity | None:
        """
        Get active custom motivation quote for organization.
        """
        sql = text(
            f"""
            SELECT * FROM {self.table_name}
            WHERE organization_id = :organization_id
            AND is_sys_default = false
            AND deleted_at IS NULL
            AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
            """
        )

        try:
            result = await self.session.execute(
                sql,
                {
                    "organization_id": organization_id,
                },
            )
            row = result.mappings().first()
            return self.to_entity(dict(row)) if row else None
        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to get active custom motivation quote",
                internal_details=str(e),
            ) from e

    async def get_active_system_quote(self) -> MotivationQuoteEntity | None:
        """
        Get active system default motivation quote.
        """
        sql = text(
            f"""
            SELECT * FROM {self.table_name}
            WHERE organization_id IS NULL
            AND is_sys_default = true
            AND status = 'active'
            AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT 1
            """
        )

        try:
            result = await self.session.execute(sql)
            row = result.mappings().first()
            return self.to_entity(dict(row)) if row else None
        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to get active system motivation quote",
                internal_details=str(e),
            ) from e

    async def get_reactable_quote(
        self,
        organization_id: int,
        quote_id: int,
    ) -> MotivationQuoteEntity | None:
        """
        Get quote that can be reacted to.

        It allows:
        1. Custom quote of the current organization
        2. Global system/default quote with organization_id NULL
        """
        sql = text(
            f"""
            SELECT * FROM {self.table_name}
            WHERE id = :quote_id
            AND deleted_at IS NULL
            AND (
                organization_id = :organization_id
                OR organization_id IS NULL
            )
            LIMIT 1
            """
        )

        try:
            result = await self.session.execute(
                sql,
                {
                    "organization_id": organization_id,
                    "quote_id": quote_id,
                },
            )
            row = result.mappings().first()
            return self.to_entity(dict(row)) if row else None
        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to get reactable motivation quote",
                internal_details=str(e),
            ) from e

    async def get_reactable_quote_by_uuid(
        self,
        organization_id: int,
        quote_uuid: str,
    ) -> MotivationQuoteEntity | None:
        """
        Get quote that can be reacted to by uuid.

        It allows:
        1. Custom quote of the current organization
        2. Global system/default quote with organization_id NULL
        """
        sql = text(
            f"""
            SELECT * FROM {self.table_name}
            WHERE uuid = :quote_uuid
            AND deleted_at IS NULL
            AND (
                organization_id = :organization_id
                OR organization_id IS NULL
            )
            LIMIT 1
            """
        )

        try:
            result = await self.session.execute(
                sql,
                {
                    "organization_id": organization_id,
                    "quote_uuid": quote_uuid,
                },
            )
            row = result.mappings().first()
            return self.to_entity(dict(row)) if row else None

        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to get reactable motivation quote by uuid",
                internal_details=str(e),
            ) from e

    async def list_system_quotes(
        self,
        organization_id: int,
        status: str | None = None,
        search: str | None = None,
    ) -> list[MotivationQuoteEntity]:
        """
        List global system/sample motivation quotes.
        """
        sql = f"""
            SELECT * FROM {self.table_name}
            WHERE organization_id = :organization_id
            AND is_sys_default = true
            AND deleted_at IS NULL
        """

        params: dict[str, object] = {"organization_id": organization_id}

        if status is not None:
            sql += " AND status = :status"
            params["status"] = status

        if search is not None:
            sql += " AND text ILIKE :search"
            params["search"] = f"%{search}%"

        sql += " ORDER BY created_at DESC"

        try:
            result = await self.session.execute(text(sql), params)
            rows = result.mappings().all()
            return [self.to_entity(dict(row)) for row in rows]

        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to list system motivation quotes",
                internal_details=str(e),
            ) from e

    async def get_system_quote_by_uuid(
        self,
        quote_uuid: str,
    ) -> MotivationQuoteEntity | None:
        """
        Get global system/sample motivation quote by uuid.
        """
        sql = text(
            f"""
            SELECT * FROM {self.table_name}
            WHERE uuid = :quote_uuid
            AND organization_id IS NULL
            AND is_sys_default = true
            AND deleted_at IS NULL
            LIMIT 1
            """
        )

        try:
            result = await self.session.execute(
                sql,
                {
                    "quote_uuid": quote_uuid,
                },
            )
            row = result.mappings().first()
            return self.to_entity(dict(row)) if row else None

        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to get system motivation quote",
                internal_details=str(e),
            ) from e

    async def list_active_custom_quotes_for_preview(
        self,
        organization_id: int,
        limit: int = 3,
    ) -> list[MotivationQuoteEntity]:
        """
        List active custom motivation quotes for preview slider.

        Custom quotes are organization-specific and are prioritized
        over system quotes in preview/slider flow.
        """
        sql = text(
            f"""
            SELECT * FROM {self.table_name}
            WHERE organization_id = :organization_id
            AND is_sys_default = false
            AND status = 'active'
            AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT :limit
            """
        )

        try:
            result = await self.session.execute(
                sql,
                {
                    "organization_id": organization_id,
                    "limit": limit,
                },
            )
            rows = result.mappings().all()
            return [self.to_entity(dict(row)) for row in rows]

        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to list custom motivation quotes for preview",
                internal_details=str(e),
            ) from e

    async def list_active_system_quotes_for_preview(
        self,
        limit: int = 3,
    ) -> list[MotivationQuoteEntity]:
        """
        List active system motivation quotes for preview slider.

        These are used only when the organization has no active custom quotes.
        """
        sql = text(
            f"""
            SELECT * FROM {self.table_name}
            WHERE organization_id IS NULL
            AND is_sys_default = true
            AND status = 'active'
            AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT :limit
            """
        )

        try:
            result = await self.session.execute(
                sql,
                {
                    "limit": limit,
                },
            )
            rows = result.mappings().all()
            return [self.to_entity(dict(row)) for row in rows]

        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to list system motivation quotes for preview",
                internal_details=str(e),
            ) from e
