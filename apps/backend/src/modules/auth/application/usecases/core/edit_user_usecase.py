from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.presentation.schemas.auth_schemas import EditProfileRequestSchema
from src.shared.exceptions.base_exceptions import DomainError, ServerError
from src.shared.mediator.mediator import mediator
from src.shared.infrastructure.country.country_reader import CountryReader


class EditUserUseCase:
    """
    Use case for editing a user.
    """

    def __init__(
        self, user_domain_service: UserDomainService, country_reader: CountryReader
    ):
        self.user_domain_service = user_domain_service
        self.country_reader = country_reader

    async def execute(
        self, user_id: int, payload: EditProfileRequestSchema
    ) -> UserEntity:
        """
        Executes the use case to edit a user.
        """

        try:
            user = await self.user_domain_service.get_user_by_id(user_id)
            if not user or not user.id:
                raise ServerError(
                    error="Error while editing the user",
                    internal_details=f"No user found with ID {user_id}",
                )

            fields = payload.model_dump(exclude_unset=True)
            if not fields:
                return user

            if "country_uuid" in fields:
                country = await self.country_reader.get_country_by_uuid(
                    fields["country_uuid"]
                )
                if not country:
                    raise DomainError(
                        error="Invalid country UUID",
                        internal_details=f"No country found with UUID {fields['country_uuid']}",
                    )
                fields["country_id"] = country.id
                del fields["country_uuid"]

            for key, value in fields.items():
                setattr(user, key, value)

            updated_user = await self.user_domain_service.update_user(user)

            for event in updated_user.pull_events():
                await mediator.publish(event)

            return updated_user
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while editing the user",
                internal_details=str(e),
            )
