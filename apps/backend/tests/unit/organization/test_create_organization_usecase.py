from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def create_organization_usecase():
    from src.modules.organization.application.usecases.core.create_organization_usecase import (
        CreateOrganizationUseCase,
    )

    mock_organization_domain_service = AsyncMock()
    mock_organization_member_domain_service = AsyncMock()
    mock_organization_onboarding_domain_service = AsyncMock()

    return CreateOrganizationUseCase(
        organization_domain_service=mock_organization_domain_service,
        organization_member_domain_service=mock_organization_member_domain_service,
        organization_onboarding_domain_service=mock_organization_onboarding_domain_service,
    )


def _make_organization(**overrides):
    from src.modules.organization.domain.entities.organization_entity import (
        OrganizationEntity,
    )

    data = {
        "id": 1,
        "name": "Test Org",
        "type": "external",
        "slug": "test-org",
        "domain": "example.com",
        "owner_id": 1,
    }
    data.update(overrides)
    return OrganizationEntity(**data)


def _make_onboarding(**overrides):
    from src.modules.organization.domain.entities.organization_onboarding_entity import (
        OrganizationOnboardingEntity,
    )

    data = {
        "id": 1,
        "organization_id": 1,
        "size_range": "11-50",
        "use_case": ["team collaboration"],
        "industry": "technology",
        "previous_tool": "intercom",
    }
    data.update(overrides)
    return OrganizationOnboardingEntity(**data)


def _make_member(**overrides):
    from src.modules.organization.domain.entities.organization_member_entity import (
        OrganizationMemberEntity,
    )

    data = {
        "id": 1,
        "organization_id": 1,
        "user_id": 42,
        "status": "active",
    }
    data.update(overrides)
    return OrganizationMemberEntity(**data)


def _make_payload(**overrides):
    from src.modules.organization.presentation.schemas.organization_schemas import (
        CreateOrganizationOnboardingRequestSchema,
        CreateOrganizationRequestSchema,
    )

    data = {
        "name": "Test Org",
        "domain": "example.com",
        "onboarding": CreateOrganizationOnboardingRequestSchema(
            size_range="11-50",
            use_case=["team collaboration"],
            industry="technology",
            previous_tool="intercom",
        ),
    }
    data.update(overrides)
    return CreateOrganizationRequestSchema(**data)


@pytest.mark.asyncio
async def test_execute_creates_organization_successfully(
    create_organization_usecase,
):
    payload = _make_payload()
    org = _make_organization()
    onboarding = _make_onboarding()
    member = _make_member()

    create_organization_usecase.organization_domain_service.create_organization = (
        AsyncMock(return_value=org)
    )
    create_organization_usecase.organization_onboarding_domain_service.create_organization_onboarding = AsyncMock(
        return_value=onboarding
    )
    create_organization_usecase.organization_member_domain_service.add_member = (
        AsyncMock(return_value=member)
    )

    with patch(
        "src.modules.organization.application.usecases.core.create_organization_usecase.mediator"
    ) as mock_mediator:
        mock_mediator.publish = AsyncMock()

        result = await create_organization_usecase.execute(payload=payload, actor_id=42)

    assert result == {
        "organization_uuid": org.uuid,
        "organization_slug": org.slug,
    }

    create_organization_usecase.organization_domain_service.create_organization.assert_awaited_once()
    create_organization_usecase.organization_onboarding_domain_service.create_organization_onboarding.assert_awaited_once()
    create_organization_usecase.organization_member_domain_service.add_member.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_raises_create_error_when_organization_creation_fails(
    create_organization_usecase,
):
    from src.shared.exceptions.base_exceptions import CreateError

    payload = _make_payload()
    org = _make_organization(id=None)

    create_organization_usecase.organization_domain_service.create_organization = (
        AsyncMock(return_value=org)
    )

    with pytest.raises(CreateError):
        await create_organization_usecase.execute(payload=payload, actor_id=42)


@pytest.mark.asyncio
async def test_execute_re_raises_domain_error_from_organization_service(
    create_organization_usecase,
):
    from src.shared.exceptions.base_exceptions import DomainError

    payload = _make_payload()

    create_organization_usecase.organization_domain_service.create_organization = (
        AsyncMock(side_effect=DomainError(error="domain error"))
    )

    with pytest.raises(DomainError):
        await create_organization_usecase.execute(payload=payload, actor_id=42)


@pytest.mark.asyncio
async def test_execute_re_raises_domain_error_from_onboarding(
    create_organization_usecase,
):
    from src.shared.exceptions.base_exceptions import DomainError

    payload = _make_payload()
    org = _make_organization()

    create_organization_usecase.organization_domain_service.create_organization = (
        AsyncMock(return_value=org)
    )
    create_organization_usecase.organization_onboarding_domain_service.create_organization_onboarding = AsyncMock(
        side_effect=DomainError(error="domain error")
    )

    with pytest.raises(DomainError):
        await create_organization_usecase.execute(payload=payload, actor_id=42)


@pytest.mark.asyncio
async def test_execute_re_raises_domain_error_from_membership(
    create_organization_usecase,
):
    from src.shared.exceptions.base_exceptions import DomainError

    payload = _make_payload()
    org = _make_organization()
    onboarding = _make_onboarding()

    create_organization_usecase.organization_domain_service.create_organization = (
        AsyncMock(return_value=org)
    )
    create_organization_usecase.organization_onboarding_domain_service.create_organization_onboarding = AsyncMock(
        return_value=onboarding
    )
    create_organization_usecase.organization_member_domain_service.add_member = (
        AsyncMock(side_effect=DomainError(error="domain error"))
    )

    with pytest.raises(DomainError):
        await create_organization_usecase.execute(payload=payload, actor_id=42)


@pytest.mark.asyncio
async def test_execute_wraps_unexpected_error_in_server_error(
    create_organization_usecase,
):
    from src.shared.exceptions.base_exceptions import ServerError

    payload = _make_payload()

    create_organization_usecase.organization_domain_service.create_organization = (
        AsyncMock(side_effect=ValueError("unexpected"))
    )

    with pytest.raises(ServerError):
        await create_organization_usecase.execute(payload=payload, actor_id=42)


def test_get_slug_from_name(create_organization_usecase):
    assert create_organization_usecase._get_slug_from_name("Test Org") == "test-org"
    assert (
        create_organization_usecase._get_slug_from_name("  My Company  ")
        == "my-company"
    )
    assert create_organization_usecase._get_slug_from_name("hello") == "hello"
