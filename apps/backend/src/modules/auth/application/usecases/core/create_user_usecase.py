from src.core.config.settings import config
from src.modules.auth.domain.entities.user_account_entity import UserAccountEntity
from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.entities.user_session_entity import UserSessionEntity
from src.modules.auth.domain.events.auth_domain_events import UserCreatedEvent
from src.modules.auth.domain.services.user_account_domain_service import (
    UserAccountDomainService,
)
from src.modules.auth.domain.services.user_domain_service import UserDomainService
from src.modules.auth.domain.services.user_session_domain_service import (
    UserSessionDomainService,
)
from src.modules.auth.domain.services.user_token_domain_service import (
    UserTokenDomainService,
)
from src.modules.auth.presentation.schemas.auth_schemas import SignupRequestSchema
from src.shared.exceptions.base_exceptions import DomainError, InvalidError, ServerError
from src.shared.infrastructure.country.country_reader import CountryReader
from src.shared.infrastructure.geoip.geoip_service import GeoIPService
from src.shared.infrastructure.hasher.hasher import HasherService
from src.shared.mediator.mediator import mediator
from src.shared.infrastructure.captcha import captcha


class CreateUserUseCase:
    """
    Use case for creating a new user.
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        user_account_domain_service: UserAccountDomainService,
        user_session_domain_service: UserSessionDomainService,
        user_token_domain_service: UserTokenDomainService,
        hasher_service: HasherService,
        geoip_service: GeoIPService,
        country_reader: CountryReader,
    ):
        self.user_domain_service = user_domain_service
        self.user_account_domain_service = user_account_domain_service
        self.user_session_domain_service = user_session_domain_service
        self.user_token_domain_service = user_token_domain_service
        self.hasher_service = hasher_service
        self.geoip_service = geoip_service
        self.country_reader = country_reader
        self.captcha = captcha

    async def execute(
        self, payload: SignupRequestSchema, ip_address: str | None = None
    ):
        """
        Executes the use case to create a new user.

        1. Checks if a user with the same email, username already exists. If so, raises a ValueError.
        2. Checks if email is temp email
        3. Checks if email domain is valid
        4. Resolves the user's country from their signup IP (best-effort).
        5. Creates a new user with the provided email and a generated username and avatar background.
        6. Returns user/session payload so the API layer can publish follow-up events
           after a successful commit.
        """
        try:
            if config.ENABLE_CAPTCHA and not await self.captcha.verify(
                token=payload.captcha_token, ip=ip_address
            ):
                raise InvalidError(
                    error="Captcha verification failed",
                    errors={"captcha_token": "Captcha verification failed"},
                )
            country_id = await self._resolve_country_id(ip_address)

            user = UserEntity(
                username=UserEntity.generate_username(payload.email),
                email=payload.email.lower(),
                avatar_bg=UserEntity.generate_random_avatar_bg(),
                status="active",
                country_id=country_id,
            )
            new_user = await self.user_domain_service.create_user(user)
            if not new_user.id:
                raise ServerError(error="Failed to create user")

            _ = await self._handle_user_account_creation(new_user.id, payload.password)
            session = await self._handle_user_session_creation(new_user.id)

            token = await self.user_token_domain_service.create_user_token(
                user_id=new_user.id,
                type="email_verification",
                expiry_minutes=config.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
            )

            new_user.add_event(
                UserCreatedEvent(
                    user_id=new_user.id,
                    email=new_user.email,
                    username=new_user.username,
                    token=token,
                )
            )

            ## Emitting events
            for event in new_user.pull_events():
                await mediator.publish(event)

            return {
                "user_id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "session_uuid": session.uuid,
                "session_expires_at": session.expires_at.isoformat(),
                "token": token,
            }

        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating the user",
                internal_details=str(e),
            ) from e

    async def _resolve_country_id(self, ip_address: str | None) -> int | None:
        """
        Best-effort resolution of the user's country from their signup IP:
        geolocate the IP, then map the ISO alpha-2 code to a sys_countries row.
        Returns None when geolocation is unavailable or no matching country
        exists - this must never block signup.
        """
        location = self.geoip_service.lookup(ip_address)
        if not location or not location.country_iso:
            return None

        country = await self.country_reader.get_country_by_iso_code_2(
            location.country_iso
        )
        return country.id if country else None

    async def _handle_user_account_creation(self, user_id: int, password: str):
        """
        Handles the creation of the user account associated with the user entity.
        """
        try:
            account_entity = UserAccountEntity(
                type="credentials",
                user_id=user_id,
                hashed_password=self.hasher_service.hash(password),
            )
            return await self.user_account_domain_service.create_user_account(
                account_entity
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating the user account",
                internal_details=str(e),
            ) from e

    async def _handle_user_session_creation(self, user_id: int) -> UserSessionEntity:
        """
        Handles the creation of a user session for the newly created user.
        """
        try:
            session_entity = UserSessionEntity(
                user_id=user_id, expires_at=UserSessionEntity.set_expiration()
            )
            return await self.user_session_domain_service.create_user_session(
                session_entity
            )
        except DomainError:
            raise
        except Exception as e:
            raise ServerError(
                error="An error occurred while creating the user session",
                internal_details=str(e),
            ) from e
