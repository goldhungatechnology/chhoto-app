from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.response import CustomResponse as cr
from src.shared.infrastructure.db import get_async_session

router = APIRouter()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
)
async def login(
    db: AsyncSession = Depends(get_async_session),
):
    """
    User login endpoint.
    TODO: Implement credential verification, session creation, and setting secure cookies.
    """
    # Example instantiation:
    # auth_container = get_auth_container(db)
    # usecase = auth_container.login_user_usecase()
    # result = await usecase.execute(payload)
    return cr.success(
        data={"todo": "Implement login logic"},
        message="Login endpoint scaffolding active",
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
async def register(
    db: AsyncSession = Depends(get_async_session),
):
    """
    User registration endpoint.
    TODO: Implement new user validation, hashing, record persistence, and triggering verification mails.
    """
    return cr.success(
        data={"todo": "Implement registration logic"},
        message="Register endpoint scaffolding active",
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
)
async def logout(
    db: AsyncSession = Depends(get_async_session),
):
    """
    User logout endpoint.
    TODO: Revoke session, clear cookie.
    """
    return cr.success(
        data={"todo": "Implement logout logic"},
        message="Logout endpoint scaffolding active",
    )
