from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.db import get_async_session
from src.shared.infrastructure.uow.base_uow import BaseUOW
from src.core.utils.response import CustomResponse as cr
from src.shared.models.country.country_model import CountryModel

public_router = APIRouter(tags=["Countries"])

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@public_router.get("/")
async def get_countries(session: AsyncSessionDep):
    """
    Endpoint to get all countries
     - Returns a list of countries with their details.
     - Each country includes its name, ISO codes, and phone code.
     - This endpoint is public and does not require authentication.
     - Useful for populating country dropdowns or selection lists in the frontend.
     - Response format:
       [
         {
           "name": "United States",
           "iso_code_2": "US",
           "iso_code_3": "USA",
           "phone_code": "+1"
         },
         ...
       ]
    """

    async with BaseUOW(session):
        try:
            table_name = CountryModel.__tablename__
            sql = text(
                f"SELECT uuid,name, iso_code_2, iso_code_3, phone_code FROM {table_name} WHERE deleted_at IS NULL"
            )
            result = await session.execute(sql)
            countries = result.fetchall()
            data = [
                {
                    "uuid": country.uuid,
                    "name": country.name,
                    "iso_code_2": country.iso_code_2,
                    "iso_code_3": country.iso_code_3,
                    "phone_code": country.phone_code,
                }
                for country in countries
            ]
        except Exception as e:
            raise ServerError(
                error="Failed to retrieve countries", internal_details=str(e)
            ) from e

    return cr.success(data=data, message="Countries retrieved successfully")
