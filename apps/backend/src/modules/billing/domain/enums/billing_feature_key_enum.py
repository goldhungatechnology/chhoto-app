from enum import StrEnum


class BillingFeatureKey(StrEnum):
    """
    Billing feature keys used for plan limits and usage tracking.
    """

    AGENTS = "agents"
    TICKETS = "tickets"
    STORAGE_MB = "storage_mb"
    ROLES = "roles"
