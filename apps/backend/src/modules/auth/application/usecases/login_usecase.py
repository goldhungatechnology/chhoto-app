from src.modules.auth.domain.repositories.user_repository import IUserRepository

# TODO: Create input schemas/DTOs and return types


class LoginUseCase:
    """
    Orchestrates the login workflow: verifying credentials, generating sessions,
    and triggering notifications or audit entries.
    """

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str, password: str) -> dict:
        """
        Executes the login process.
        TODO: Implement credentials verification, MFA check, and session generation.
        """
        # Example flow:
        # user = await self.user_repository.get_by_email(email)
        # if not user or not verify_password(password, user.password_hash):
        #     raise InvalidCredentialsError()
        # session = await self.session_service.create_session(user.id)
        # return session
        return {"message": "TODO: Implement login use case"}
