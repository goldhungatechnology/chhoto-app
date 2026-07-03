from pydantic import BaseModel


class CreateOrganizationFeatureUsageRequestSchema(BaseModel):
    """
    Request schema for creating organization feature usage.
    """

    subscription_id: int
    feature_key: str
    used_value: int
