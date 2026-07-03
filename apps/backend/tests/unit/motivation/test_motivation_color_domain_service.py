from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


CONFIG_ID = 1
ACTOR_ID = 1


@pytest_asyncio.fixture
async def motivation_color_domain_service():
    from src.modules.motivation.domain.services.motivation_color_domain_service import (
        MotivationColorDomainService,
    )

    mock_repo = AsyncMock()
    mock_repo.session = None
    mock_repo.add = AsyncMock()
    mock_repo.delete_by_id = AsyncMock()
    mock_repo.list_by_config_id = AsyncMock()

    return MotivationColorDomainService(repository=mock_repo)


def make_color(**kwargs):
    from src.modules.motivation.domain.entities.motivation_color_entity import (
        MotivationColorEntity,
    )

    data = {
        "id": 1,
        "uuid": "color-uuid",
        "config_id": CONFIG_ID,
        "color_code": "#7C3AED",
        "created_by_id": ACTOR_ID,
        "updated_by_id": ACTOR_ID,
    }
    data.update(kwargs)

    return MotivationColorEntity(**data)


@pytest.mark.asyncio
async def test_list_colors_returns_empty_when_no_colors_exist(
    motivation_color_domain_service,
):
    motivation_color_domain_service.repository.list_by_config_id = AsyncMock(
        return_value=[]
    )

    colors = await motivation_color_domain_service.list_colors(
        config_id=CONFIG_ID,
        actor_id=ACTOR_ID,
    )

    assert colors == []
    motivation_color_domain_service.repository.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_colors_returns_existing_colors_newest_first(
    motivation_color_domain_service,
):
    existing_colors = [
        make_color(id=1, color_code="#111111"),
        make_color(id=2, color_code="#222222"),
        make_color(id=3, color_code="#333333"),
    ]

    motivation_color_domain_service.repository.list_by_config_id = AsyncMock(
        return_value=existing_colors
    )

    colors = await motivation_color_domain_service.list_colors(
        config_id=CONFIG_ID,
        actor_id=ACTOR_ID,
    )

    assert colors == list(reversed(existing_colors))
    motivation_color_domain_service.repository.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_color_with_empty_color_code_raises_invalid_error(
    motivation_color_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    with pytest.raises(InvalidError):
        await motivation_color_domain_service.add_color(
            config_id=CONFIG_ID,
            color_code="",
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_add_color_adds_color_when_count_is_less_than_five(
    motivation_color_domain_service,
):
    existing_colors = [
        make_color(id=1, color_code="#111111"),
    ]
    new_color = make_color(id=2, color_code="#ABCDEF")

    motivation_color_domain_service.repository.list_by_config_id = AsyncMock(
        return_value=existing_colors
    )
    motivation_color_domain_service.repository.add = AsyncMock(return_value=new_color)

    color = await motivation_color_domain_service.add_color(
        config_id=CONFIG_ID,
        color_code="#ABCDEF",
        actor_id=ACTOR_ID,
    )

    assert color == new_color
    motivation_color_domain_service.repository.delete_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_color_deletes_oldest_when_colors_are_already_five(
    motivation_color_domain_service,
):
    existing_colors = [
        make_color(id=1, color_code="#111111"),
        make_color(id=2, color_code="#222222"),
        make_color(id=3, color_code="#333333"),
        make_color(id=4, color_code="#444444"),
        make_color(id=5, color_code="#555555"),
    ]

    new_color = make_color(id=6, color_code="#666666")

    motivation_color_domain_service.repository.list_by_config_id = AsyncMock(
        return_value=existing_colors
    )
    motivation_color_domain_service.repository.add = AsyncMock(return_value=new_color)

    color = await motivation_color_domain_service.add_color(
        config_id=CONFIG_ID,
        color_code="#666666",
        actor_id=ACTOR_ID,
    )

    assert color == new_color
    motivation_color_domain_service.repository.delete_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_add_color_deletes_extra_old_colors_when_more_than_five_exist(
    motivation_color_domain_service,
):
    existing_colors = [
        make_color(id=1, color_code="#111111"),
        make_color(id=2, color_code="#222222"),
        make_color(id=3, color_code="#333333"),
        make_color(id=4, color_code="#444444"),
        make_color(id=5, color_code="#555555"),
        make_color(id=6, color_code="#666666"),
        make_color(id=7, color_code="#777777"),
    ]

    new_color = make_color(id=8, color_code="#888888")

    motivation_color_domain_service.repository.list_by_config_id = AsyncMock(
        side_effect=[
            existing_colors,
            existing_colors,
        ]
    )
    motivation_color_domain_service.repository.add = AsyncMock(return_value=new_color)

    color = await motivation_color_domain_service.add_color(
        config_id=CONFIG_ID,
        color_code="#888888",
        actor_id=ACTOR_ID,
    )

    assert color == new_color
    assert motivation_color_domain_service.repository.delete_by_id.await_count == 3


@pytest.mark.asyncio
async def test_add_color_raises_invalid_error_when_oldest_color_id_missing(
    motivation_color_domain_service,
):
    from src.shared.exceptions.base_exceptions import InvalidError

    existing_colors = [
        make_color(id=None, color_code="#111111"),
        make_color(id=2, color_code="#222222"),
        make_color(id=3, color_code="#333333"),
        make_color(id=4, color_code="#444444"),
        make_color(id=5, color_code="#555555"),
    ]

    motivation_color_domain_service.repository.list_by_config_id = AsyncMock(
        side_effect=[
            existing_colors,
            existing_colors,
        ]
    )

    with pytest.raises(InvalidError):
        await motivation_color_domain_service.add_color(
            config_id=CONFIG_ID,
            color_code="#666666",
            actor_id=ACTOR_ID,
        )


@pytest.mark.asyncio
async def test_add_color_success_when_less_than_five_colors_exist(
    motivation_color_domain_service,
):
    existing_colors = [
        make_color(id=1, color_code="#111111"),
        make_color(id=2, color_code="#222222"),
    ]

    new_color = make_color(id=3, color_code="#333333")

    motivation_color_domain_service.repository.list_by_config_id = AsyncMock(
        side_effect=[
            existing_colors,
            existing_colors,
        ]
    )
    motivation_color_domain_service.repository.add = AsyncMock(return_value=new_color)

    color = await motivation_color_domain_service.add_color(
        config_id=CONFIG_ID,
        color_code="#333333",
        actor_id=ACTOR_ID,
    )

    assert color == new_color
    motivation_color_domain_service.repository.delete_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_color_strips_color_code(
    motivation_color_domain_service,
):
    existing_colors = [
        make_color(id=1, color_code="#111111"),
    ]

    new_color = make_color(id=2, color_code="#ABCDEF")

    motivation_color_domain_service.repository.list_by_config_id = AsyncMock(
        side_effect=[
            existing_colors,
            existing_colors,
        ]
    )
    motivation_color_domain_service.repository.add = AsyncMock(return_value=new_color)

    color = await motivation_color_domain_service.add_color(
        config_id=CONFIG_ID,
        color_code="   #ABCDEF   ",
        actor_id=ACTOR_ID,
    )

    assert color.color_code == "#ABCDEF"
