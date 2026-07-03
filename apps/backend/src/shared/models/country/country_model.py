from src.shared.infrastructure.model.base_model import BaseModel
from src.shared.infrastructure.model.soft_delete_mixin_model import SoftDeleteMixinModel

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class CountryModel(BaseModel, SoftDeleteMixinModel):
    """
    sqlalchemy model representing the Country entity in the database.
    """

    __tablename__ = "sys_countries"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    iso_code_2: Mapped[str] = mapped_column(String(2), nullable=False)
    iso_code_3: Mapped[str] = mapped_column(String(3), nullable=False)
    phone_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
