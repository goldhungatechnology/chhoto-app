from pydantic import BaseModel


class CreateBillingPlanRequestSchema(BaseModel):
    """
    Request schema for creating a billing plan.
    """

    name: str
    price: float
    currency: str
    interval: str
    is_active: bool = True
