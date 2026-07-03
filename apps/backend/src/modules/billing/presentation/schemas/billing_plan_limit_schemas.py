from pydantic import BaseModel


class CreateBillingPlanLimitRequestSchema(BaseModel):
    """
    Request schema for creating a billing plan limit.
    """

    plan_id: int
    feature_key: str
    limit_value: int | None = None
    is_unlimited: bool = False
