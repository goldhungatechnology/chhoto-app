from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


ORG_ID = 1
MEMBER_ID = 1
ACTOR_ID = 1
QUOTE_ID = 10
REACTION_ID = 1
QUOTE_UUID = "10d7e708-7bdd-4184-980a-cf05c815f8cf"


@pytest_asyncio.fixture
async def motivation_quote_reaction_domain_service():
    from src.modules.motivation.domain.services.motivation_quote_reaction_domain_service import (
        MotivationQuoteReactionDomainService,
    )

    mock_reaction_repo = AsyncMock()
    mock_reaction_repo.session = None
    mock_reaction_repo.add = AsyncMock()
    mock_reaction_repo.update = AsyncMock()
    mock_reaction_repo.get_by_member_and_quote = AsyncMock()
    mock_reaction_repo.list_by_quote_id = AsyncMock()

    mock_quote_repo = AsyncMock()
    mock_quote_repo.get_reactable_quote_by_uuid = AsyncMock()

    mock_config_repo = AsyncMock()
    mock_config_repo.get_by_organization_id = AsyncMock()

    return MotivationQuoteReactionDomainService(
        reaction_repository=mock_reaction_repo,
        quote_repository=mock_quote_repo,
        config_repository=mock_config_repo,
    )


def make_quote(**kwargs):
    from src.modules.motivation.domain.entities.motivation_quote_entity import (
        MotivationQuoteEntity,
    )

    data = {
        "id": QUOTE_ID,
        "uuid": QUOTE_UUID,
        "organization_id": ORG_ID,
        "context": "Stay focused.",
        "author_name": "Author",
        "is_sys_default": False,
        "status": "active",
        "font_style": "arial",
        "theme_color": "#7C3AED",
        "bg_image": None,
    }
    data.update(kwargs)

    return MotivationQuoteEntity(**data)


def make_reaction(**kwargs):
    from src.modules.motivation.domain.entities.motivation_quote_reaction_entity import (
        MotivationQuoteReactionEntity,
    )

    data = {
        "id": REACTION_ID,
        "organization_id": ORG_ID,
        "member_id": MEMBER_ID,
        "quote_id": QUOTE_ID,
        "reaction_type": "like",
    }
    data.update(kwargs)

    return MotivationQuoteReactionEntity(**data)


def make_config(**kwargs):
    from src.modules.motivation.domain.entities.daily_motivation_config_entity import (
        DailyMotivationConfigEntity,
    )

    data = {
        "id": 1,
        "organization_id": ORG_ID,
        "sys_quote_source": True,
        "is_enabled": True,
        "allow_reactions": True,
    }
    data.update(kwargs)

    return DailyMotivationConfigEntity(**data)


@pytest.mark.asyncio
async def test_add_or_update_reaction_with_empty_reaction_type_raises_invalid_error(
    motivation_quote_reaction_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    with pytest.raises(InvalidError):
        await motivation_quote_reaction_domain_service.add_or_update_reaction(
            organization_id=ORG_ID,
            member_id=MEMBER_ID,
            quote_uuid=QUOTE_UUID,
            reaction_type="",
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_add_or_update_reaction_when_reactions_disabled_raises_invalid_error(
    motivation_quote_reaction_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    motivation_quote_reaction_domain_service.config_repository.get_by_organization_id = AsyncMock(
        return_value=make_config(allow_reactions=False)
    )

    with pytest.raises(InvalidError):
        await motivation_quote_reaction_domain_service.add_or_update_reaction(
            organization_id=ORG_ID,
            member_id=MEMBER_ID,
            quote_uuid=QUOTE_UUID,
            reaction_type="like",
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_add_or_update_reaction_quote_not_found_raises_invalid_error(
    motivation_quote_reaction_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    motivation_quote_reaction_domain_service.config_repository.get_by_organization_id = AsyncMock(
        return_value=make_config(allow_reactions=True)
    )
    motivation_quote_reaction_domain_service.quote_repository.get_reactable_quote_by_uuid = AsyncMock(
        return_value=None
    )

    with pytest.raises(InvalidError):
        await motivation_quote_reaction_domain_service.add_or_update_reaction(
            organization_id=ORG_ID,
            member_id=MEMBER_ID,
            quote_uuid=QUOTE_UUID,
            reaction_type="like",
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_add_or_update_reaction_to_inactive_quote_raises_invalid_error(
    motivation_quote_reaction_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    motivation_quote_reaction_domain_service.config_repository.get_by_organization_id = AsyncMock(
        return_value=make_config(allow_reactions=True)
    )
    motivation_quote_reaction_domain_service.quote_repository.get_reactable_quote_by_uuid = AsyncMock(
        return_value=make_quote(status="inactive")
    )

    with pytest.raises(InvalidError):
        await motivation_quote_reaction_domain_service.add_or_update_reaction(
            organization_id=ORG_ID,
            member_id=MEMBER_ID,
            quote_uuid=QUOTE_UUID,
            reaction_type="like",
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_add_or_update_reaction_creates_new_reaction_success(
    motivation_quote_reaction_domain_service,
):
    saved_reaction = make_reaction(reaction_type="like")

    motivation_quote_reaction_domain_service.config_repository.get_by_organization_id = AsyncMock(
        return_value=make_config(allow_reactions=True)
    )
    motivation_quote_reaction_domain_service.quote_repository.get_reactable_quote_by_uuid = AsyncMock(
        return_value=make_quote(status="active")
    )
    motivation_quote_reaction_domain_service.reaction_repository.get_by_member_and_quote = AsyncMock(
        return_value=None
    )
    motivation_quote_reaction_domain_service.reaction_repository.add = AsyncMock(
        return_value=saved_reaction
    )

    result = await motivation_quote_reaction_domain_service.add_or_update_reaction(
        organization_id=ORG_ID,
        member_id=MEMBER_ID,
        quote_uuid=QUOTE_UUID,
        reaction_type="like",
        actor_id=ACTOR_ID,
    )

    assert result == saved_reaction
    assert result.reaction_type == "like"
    motivation_quote_reaction_domain_service.reaction_repository.add.assert_awaited_once()
    motivation_quote_reaction_domain_service.reaction_repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_or_update_reaction_updates_existing_reaction_success(
    motivation_quote_reaction_domain_service,
):
    existing_reaction = make_reaction(reaction_type="like")

    motivation_quote_reaction_domain_service.config_repository.get_by_organization_id = AsyncMock(
        return_value=make_config(allow_reactions=True)
    )
    motivation_quote_reaction_domain_service.quote_repository.get_reactable_quote_by_uuid = AsyncMock(
        return_value=make_quote(status="active")
    )
    motivation_quote_reaction_domain_service.reaction_repository.get_by_member_and_quote = AsyncMock(
        return_value=existing_reaction
    )
    motivation_quote_reaction_domain_service.reaction_repository.update = AsyncMock(
        return_value=existing_reaction
    )

    result = await motivation_quote_reaction_domain_service.add_or_update_reaction(
        organization_id=ORG_ID,
        member_id=MEMBER_ID,
        quote_uuid=QUOTE_UUID,
        reaction_type="love",
        actor_id=ACTOR_ID,
    )

    assert result == existing_reaction
    assert result.reaction_type == "love"
    assert result.updated_by_id == ACTOR_ID
    motivation_quote_reaction_domain_service.reaction_repository.update.assert_awaited_once()
    motivation_quote_reaction_domain_service.reaction_repository.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_or_update_reaction_works_when_config_not_found(
    motivation_quote_reaction_domain_service,
):
    saved_reaction = make_reaction(reaction_type="like")

    motivation_quote_reaction_domain_service.config_repository.get_by_organization_id = AsyncMock(
        return_value=None
    )
    motivation_quote_reaction_domain_service.quote_repository.get_reactable_quote_by_uuid = AsyncMock(
        return_value=make_quote(status="active")
    )
    motivation_quote_reaction_domain_service.reaction_repository.get_by_member_and_quote = AsyncMock(
        return_value=None
    )
    motivation_quote_reaction_domain_service.reaction_repository.add = AsyncMock(
        return_value=saved_reaction
    )

    result = await motivation_quote_reaction_domain_service.add_or_update_reaction(
        organization_id=ORG_ID,
        member_id=MEMBER_ID,
        quote_uuid=QUOTE_UUID,
        reaction_type="like",
        actor_id=ACTOR_ID,
    )

    assert result == saved_reaction


@pytest.mark.asyncio
async def test_list_quote_reactions_success(
    motivation_quote_reaction_domain_service,
):
    reactions = [
        make_reaction(id=1, reaction_type="like"),
        make_reaction(id=2, reaction_type="love"),
    ]

    motivation_quote_reaction_domain_service.quote_repository.get_reactable_quote_by_uuid = AsyncMock(
        return_value=make_quote()
    )
    motivation_quote_reaction_domain_service.reaction_repository.list_by_quote_id = (
        AsyncMock(return_value=reactions)
    )

    result = await motivation_quote_reaction_domain_service.list_quote_reactions(
        organization_id=ORG_ID,
        quote_uuid=QUOTE_UUID,
    )

    assert result == reactions
    motivation_quote_reaction_domain_service.reaction_repository.list_by_quote_id.assert_awaited_once_with(
        organization_id=ORG_ID,
        quote_id=QUOTE_ID,
    )


@pytest.mark.asyncio
async def test_list_quote_reactions_quote_not_found_raises_invalid_error(
    motivation_quote_reaction_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    motivation_quote_reaction_domain_service.quote_repository.get_reactable_quote_by_uuid = AsyncMock(
        return_value=None
    )

    with pytest.raises(InvalidError):
        await motivation_quote_reaction_domain_service.list_quote_reactions(
            organization_id=ORG_ID,
            quote_uuid=QUOTE_UUID,
        )
