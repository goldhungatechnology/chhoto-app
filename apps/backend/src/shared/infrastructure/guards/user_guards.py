from fastapi import Depends

from src.shared.infrastructure.middlewares.policy.user_policies import UserPolicies


def require_verified_email(user=Depends(lambda request: request.state.user)):
    """
    requires the user to have a verified email address. If the user's email is not verified, it raises an exception with the message "EMAIL_UNVERIFIED". This policy can be used to restrict access to certain features or actions until the user has verified their email address.
    """
    UserPolicies.require_email_verified(user)
    return user


def require_onboarding(user=Depends(lambda request: request.state.user)):
    """
    requires the user to have completed the onboarding process. If the user has not completed onboarding, it raises an exception with the message "ONBOARDING_REQUIRED". This policy can be used to ensure that users have completed necessary setup steps before accessing certain features or actions.
    """
    UserPolicies.require_onboarding(user)
    return user
