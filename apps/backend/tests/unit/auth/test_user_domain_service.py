from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def user_domain_service():
    """
    fixture for user domain service with mocked dependencies
    """

    from src.modules.auth.domain.services.user_domain_service import UserDomainService

    mock_repo = AsyncMock()
    mock_repo.get_by = AsyncMock()
    mock_repo.create = AsyncMock()

    mock_email_validator = AsyncMock()

    return UserDomainService(
        repository=mock_repo,
        email_validator=mock_email_validator,
    )


@pytest.mark.asyncio
async def test_create_user_with_temporary_email(user_domain_service):
    """
    Test that creating a user with a temporary email raises a ConflictError.
    """
    from src.modules.auth.domain.entities.user_entity import UserEntity
    from src.shared.exceptions.base_exceptions import InvalidError

    # Mock the repository's get_by method to return None (no existing user)
    user_domain_service.repository.get_by = AsyncMock(return_value=None)

    # Create a user entity with a temporary email
    temp_email_user = UserEntity(
        username="tempuser",
        email="test@mailinator.com",
        avatar_bg="#ffffff",
        status="active",
    )

    with pytest.raises(InvalidError):
        await user_domain_service.create_user(temp_email_user)


@pytest.mark.asyncio
async def test_create_user_with_invalid_domain_email(user_domain_service):
    """
    Test that creating a user with an invalid email domain raises an InvalidError.
    """
    from src.modules.auth.domain.entities.user_entity import UserEntity
    from src.shared.exceptions.base_exceptions import InvalidError

    # Mock the repository's get_by method to return None (no existing user)
    user_domain_service.repository.get_by = AsyncMock(return_value=None)

    # Mock the email validator to return False (invalid email)
    user_domain_service.email_validator.domain_exists = AsyncMock(return_value=False)

    # Create a user entity with an invalid email domain
    invalid_email_user = UserEntity(
        username="invaliduser",
        email="test@jptdm.com",
        avatar_bg="#ffffff",
        status="active",
    )

    with pytest.raises(InvalidError):
        await user_domain_service.create_user(invalid_email_user)


@pytest.mark.asyncio
async def test_create_user_with_valid_email(user_domain_service):
    """
    test that creating a user with a valid email
    """

    from src.modules.auth.domain.entities.user_entity import UserEntity

    # Mock the repository's get_by method to return None (no existing user)
    user_domain_service.repository.get_by = AsyncMock(return_value=None)

    # Mock the email validator to return False (invalid email)
    user_domain_service.email_validator.domain_exists = AsyncMock(return_value=True)

    # Create a user entity with an invalid email domain
    invalid_email_user = UserEntity(
        username="invaliduser",
        email="test@gmail.com",
        avatar_bg="#ffffff",
        status="active",
    )

    await user_domain_service.create_user(invalid_email_user)


@pytest.mark.asyncio
async def test_create_user_with_existing_email(user_domain_service):
    """
    test that creating a user with an existing email raises a ConflictError
    """
    from src.modules.auth.domain.entities.user_entity import UserEntity
    from src.shared.exceptions.base_exceptions import ConflictError

    # Mock the repository's get_by method to return an existing user
    user_domain_service.repository.get_by = AsyncMock(
        return_value=UserEntity(
            username="existinguser",
            email="test@gmail.com",
            avatar_bg="#ffffff",
            status="active",
        )
    )

    with pytest.raises(ConflictError):
        await user_domain_service.create_user(
            UserEntity(
                username="newuser",
                email="test@gmail.com",
                avatar_bg="#ffffff",
                status="active",
            )
        )


@pytest.mark.asyncio
async def test_create_user_with_existing_username(user_domain_service):
    """
    test that creating a user with an existing username raises a ConflictError
    """
    from src.modules.auth.domain.entities.user_entity import UserEntity
    from src.shared.exceptions.base_exceptions import ConflictError

    # Mock the repository's get_by method to return an existing user for email and username
    user_domain_service.repository.get_by = AsyncMock(
        side_effect=[
            None,  # No existing user for email
            UserEntity(  # Existing user for username
                username="existinguser",
                email="a@gmail.com",
                avatar_bg="#ffffff",
                status="active",
            ),
        ]
    )

    with pytest.raises(ConflictError):
        await user_domain_service.create_user(
            UserEntity(
                username="existinguser",
                email="no@gmail.com",
                avatar_bg="#ffffff",
                status="active",
            )
        )
