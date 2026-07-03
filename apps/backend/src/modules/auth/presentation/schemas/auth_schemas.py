from pydantic import BaseModel, EmailStr

# TODO: Define request/response Pydantic models.


class LoginRequestSchema(BaseModel):
    """
    Pydantic schema validation for login requests.
    """

    email: EmailStr
    password: str
