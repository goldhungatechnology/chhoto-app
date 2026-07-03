import uuid
from dataclasses import dataclass


@dataclass
class FakeUser:
    username: str = ""
    email: str = ""
    password: str = ""
    first_name: str = ""
    last_name: str = ""

    @classmethod
    def build(cls, **overrides):
        uid = uuid.uuid4().hex[:12]
        data = {
            "username": f"testuser_{uid}",
            "email": f"testuser_{uid}@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
        }
        data.update(overrides)
        return cls(**data)
