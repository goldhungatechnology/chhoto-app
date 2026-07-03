from pydantic import BaseModel


class CreateBillingSubscriptionRequestSchema(BaseModel):
    """
    Request schema for creating a billing subscription.
    """

    plan_id: int
    billing_cycle: str
    # NOTE: subscription status is intentionally NOT accepted from the client.
    # It is derived server-side so a caller cannot self-provision an active
    # paid plan or bypass the trial.
    auto_renew: bool = True
