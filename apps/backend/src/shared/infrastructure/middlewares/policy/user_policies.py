from src.shared.exceptions.base_exceptions import DomainError


class UserPolicies:
    """
    policies related to user access control. These policies can be used in various parts of the application to enforce certain conditions on user actions, such as requiring email verification, onboarding completion, or organization membership.
    """

    @staticmethod
    def require_email_verified(user):
        """
        requires the user to have a verified email address. If the user's email is not verified, it raises an exception with the message "EMAIL_UNVERIFIED". This policy can be used to restrict access to certain features or actions until the user has verified their email address.
        """
        if not user.is_email_verified():
            raise DomainError(
                errors={"code": "EMAIL_UNVERIFIED"},
                error="Email address is not verified. Please verify your email to access this feature.",
            )

    @staticmethod
    def require_onboarding(user):
        """
        requires the user to have completed the onboarding process. If the user has not completed onboarding, it raises an exception with the message "ONBOARDING_REQUIRED". This policy can be used to ensure that users have completed necessary setup steps before accessing certain features or actions.
        """
        if not user.is_onboarded:
            raise DomainError(
                errors={"code": "ONBOARDING_REQUIRED"},
                error="User has not completed onboarding. Please complete the onboarding process to access this feature.",
            )
