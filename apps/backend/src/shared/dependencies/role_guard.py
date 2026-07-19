from collections.abc import Iterable
from fastapi import Request


def require_org_role(allowed_roles: Iterable[str]):
    """
    Stub dependency that always authorizes the caller.
    """

    async def dependency(request: Request) -> None:
        pass

    return dependency
