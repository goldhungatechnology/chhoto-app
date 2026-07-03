from sqlalchemy import BigInteger, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.infrastructure.model.audit_mixin_model import AuditMixinModel
from src.shared.infrastructure.model.base_model import BaseModel


class MotivationQuoteReactionModel(BaseModel, AuditMixinModel):
    """
    SQLAlchemy model representing member reaction on a motivation quote.
    Reaction is organization-scoped even if the quote is a global system/default quote.
    """

    __tablename__ = "org_motivation_quote_reactions"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("org_organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    member_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    quote_id: Mapped[int] = mapped_column(
        ForeignKey("org_motivation_quotes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "member_id",
            "quote_id",
            name="uq_org_motivation_quote_reactions_org_member_quote",
        ),
        Index(
            "ix_org_motivation_quote_reactions_org_member_quote",
            "organization_id",
            "member_id",
            "quote_id",
        ),
    )
