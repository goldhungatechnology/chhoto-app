from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.motivation.domain.entities.motivation_color_entity import (
    MotivationColorEntity,
)
from src.modules.motivation.domain.entities.motivation_quote_entity import (
    MotivationQuoteEntity,
)
from src.modules.motivation.motivation_container import get_motivation_container

DEFAULT_MOTIVATIONS = [
    {
        "context": "The only way to do great work is to love what you do.",
        "author_name": "Steve Jobs",
        "font_style": "playfair_display",
        "theme_color": "#8B5CF6",
        "bg_image": "https://res.cloudinary.com/dnfn3i8wy/image/upload/v1782371908/Dynamic%20folders/hdks6lh1gytkeebvuivr.jpg",
    },
    {
        "context": "Believe you can and you're halfway there.",
        "author_name": "Theodore Roosevelt",
        "font_style": "georgia",
        "theme_color": "#3B82F6",
        "bg_image": "https://res.cloudinary.com/dnfn3i8wy/image/upload/v1782371908/Dynamic%20folders/hdks6lh1gytkeebvuivr.jpg",
    },
    {
        "context": "It always seems impossible until it's done.",
        "author_name": "Nelson Mandela",
        "font_style": "merriweather",
        "theme_color": "#10B981",
        "bg_image": "https://res.cloudinary.com/dnfn3i8wy/image/upload/v1782371908/Dynamic%20folders/hdks6lh1gytkeebvuivr.jpg",
    },
    {
        "context": "Act as if what you do makes a difference. It does.",
        "author_name": "William James",
        "font_style": "baskerville",
        "theme_color": "#F59E0B",
        "bg_image": "https://res.cloudinary.com/dnfn3i8wy/image/upload/v1782371908/Dynamic%20folders/hdks6lh1gytkeebvuivr.jpg",
    },
]

DEFAULT_COLORS = [
    "#7C3AED",
    "#F59E0B",
    "#059669",
    "#2563EB",
    "#7E22CE",
]


async def seed_default_quotes_for_organization(
    session: AsyncSession,
    organization_id: int,
    actor_id: int,
) -> None:
    """
    Seed default system motivation quotes, default daily config, and default colors
    for a newly created organization.
    """
    container = get_motivation_container(session=session)
    quote_repository = container.motivation_quote_repository()
    config_domain_service = container.daily_motivation_config_domain_service()
    color_repository = container.motivation_color_repository()

    for item in DEFAULT_MOTIVATIONS:
        quote = MotivationQuoteEntity(
            organization_id=organization_id,
            context=item["context"],
            author_name=item["author_name"],
            is_sys_default=True,
            status="active",
            font_style=item["font_style"],
            theme_color=item["theme_color"],
            bg_image=item["bg_image"],
            created_by_id=actor_id,
            updated_by_id=actor_id,
        )
        await quote_repository.add(quote)

    config = await config_domain_service.get_or_create_default_config(
        organization_id=organization_id,
        actor_id=actor_id,
    )

    assert config.id is not None

    for color_code in DEFAULT_COLORS:
        color = MotivationColorEntity(
            config_id=config.id,
            color_code=color_code,
            created_by_id=actor_id,
            updated_by_id=actor_id,
        )
        await color_repository.add(color)
