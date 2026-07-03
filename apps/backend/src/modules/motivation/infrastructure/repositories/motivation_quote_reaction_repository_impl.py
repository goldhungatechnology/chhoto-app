from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.modules.motivation.domain.entities.motivation_quote_reaction_entity import (
    MotivationQuoteReactionEntity,
)
from src.modules.motivation.domain.repositories.motivation_quote_reaction_repository import (
    IMotivationQuoteReactionRepository,
)
from src.modules.motivation.infrastructure.models.motivation_quote_reaction_model import (
    MotivationQuoteReactionModel,
)
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.repository.base_repository import BaseRepository


class MotivationQuoteReactionRepositoryImpl(
    BaseRepository[MotivationQuoteReactionEntity], IMotivationQuoteReactionRepository
):
    """
    SQLAlchemy implementation of the motivation quote reaction repository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.table_name = MotivationQuoteReactionModel.__tablename__
        super().__init__(session, self.table_name)

    def to_row(self, entity: MotivationQuoteReactionEntity) -> dict:
        """
        Convert MotivationQuoteReactionEntity to database row.
        """
        return {
            "id": entity.id,
            "uuid": entity.uuid,
            "organization_id": entity.organization_id,
            "member_id": entity.member_id,
            "quote_id": entity.quote_id,
            "reaction_type": entity.reaction_type,
            "created_by_id": entity.created_by_id,
            "updated_by_id": entity.updated_by_id,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def to_entity(self, row: dict) -> MotivationQuoteReactionEntity:
        """
        Convert database row to MotivationQuoteReactionEntity.
        """
        return MotivationQuoteReactionEntity(
            id=row["id"],
            uuid=row["uuid"],
            organization_id=row["organization_id"],
            member_id=row["member_id"],
            quote_id=row["quote_id"],
            reaction_type=row["reaction_type"],
            created_by_id=row.get("created_by_id"),
            updated_by_id=row.get("updated_by_id"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_by_member_and_quote(
        self,
        organization_id: int,
        member_id: int,
        quote_id: int,
    ) -> MotivationQuoteReactionEntity | None:
        """
        Get reaction by organization, member and quote.
        """
        try:
            return await self.get_by(
                organization_id=organization_id,
                member_id=member_id,
                quote_id=quote_id,
            )
        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to get motivation quote reaction",
                internal_details=str(e),
            ) from e

    async def list_by_quote_id(
        self,
        organization_id: int,
        quote_id: int,
    ) -> list[MotivationQuoteReactionEntity]:
        """
        List reactions by quote id.
        """
        sql = text(
            f"""
            SELECT * FROM {self.table_name}
            WHERE organization_id = :organization_id
            AND quote_id = :quote_id
            ORDER BY created_at DESC
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
            rows = result.mappings().all()
            return [self.to_entity(dict(row)) for row in rows]
        except SQLAlchemyError as e:
            raise ServerError(
                "Failed to list motivation quote reactions",
                internal_details=str(e),
            ) from e
