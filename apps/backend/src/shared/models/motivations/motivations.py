from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.base_model import BaseModel


class SystemMotivationModel(BaseModel):
    """
    SQLAlchemy model representing motivation-related data.
    This model serves as a base for other motivation-related models.
    """

    __tablename__ = "sys_motivations"

    context: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    font_style: Mapped[str] = mapped_column(String(100), nullable=False)
    theme_color: Mapped[str] = mapped_column(String(50), nullable=False)
    bg_image: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )
