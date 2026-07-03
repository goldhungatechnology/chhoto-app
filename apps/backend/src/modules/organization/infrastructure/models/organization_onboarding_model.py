from src.shared.infrastructure.model.base_model import BaseModel


from sqlalchemy import ARRAY, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class OrganizationOnboardingModel(BaseModel):
    """
    SQLAlchemy model for organization onboarding data. This model represents the onboarding process for an organization, including the steps completed and the current status of the onboarding process.
    """

    __tablename__ = "org_organization_onboardings"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    size_range: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default=None
    )
    use_case: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True, default=None
    )
    industry: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None
    )
    previous_tool: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
