from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.models.country.country_model import CountryModel


class CountryReader:
    """
    Lightweight reader for country data, exposed to other modules so they can
    resolve a country by id without depending on the country model directly.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_country_by_id(self, country_id: int) -> CountryModel | None:
        """
        Retrieves the country associated with the given country ID, ignoring
        soft-deleted rows. Returns None when no matching country exists.
        """
        result = await self.session.execute(
            select(CountryModel).where(
                CountryModel.id == country_id,
                CountryModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_country_by_uuid(self, country_uuid: str) -> CountryModel | None:
        """
        Retrieves the country associated with the given country UUID, ignoring
        soft-deleted rows. Returns None when no matching country exists.
        """
        result = await self.session.execute(
            select(CountryModel).where(
                CountryModel.uuid == country_uuid,
                CountryModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_country_by_iso_code_2(self, iso_code_2: str) -> CountryModel | None:
        """
        Retrieves the country matching the given ISO 3166-1 alpha-2 code
        (case-insensitive), ignoring soft-deleted rows. Returns None when no
        matching country exists.
        """
        result = await self.session.execute(
            select(CountryModel).where(
                CountryModel.iso_code_2 == iso_code_2.upper(),
                CountryModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()


def get_country_reader(session: AsyncSession) -> CountryReader:
    """
    Factory function to create a CountryReader with the necessary dependencies.
    """
    return CountryReader(session=session)
