from typing import Any, Literal, NotRequired, TypedDict

from fastapi import Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from starlette.status import HTTP_204_NO_CONTENT

from src.core.config.settings import config


class CustomSuccessResponseSchema[T](BaseModel):
    """
    Custom Success Response Schema for all APIs
    """

    success: bool
    data: T | list[T] | None
    message: str


class CustomErrorResponseSchema[T](BaseModel):
    """
    Custom Error Response Schema for all APIs
    """

    success: bool
    errors: T | list[T] | None
    error: str


class CustomResponse:
    """
    Custom responses wrapper utility
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Successful",
        status_code: int = status.HTTP_200_OK,
    ):
        """
        On success, returns success=True with data and message
        """
        if status_code == HTTP_204_NO_CONTENT:
            return Response(status_code=status_code)
        if ":" in message:
            message = message.split(":")[1]
        content = {"success": True, "message": message, "data": jsonable_encoder(data)}
        return JSONResponse(status_code=status_code, content=content)

    @staticmethod
    def error(
        errors: Any | None = None,
        error: str | None = "Unsuccessful",
        status_code: int | None = status.HTTP_400_BAD_REQUEST,
    ):
        """
        On error, returns success=False and with error description and optional error details
        """
        content = {"success": False, "error": error, "errors": jsonable_encoder(errors)}
        return JSONResponse(
            status_code=status_code or status.HTTP_400_BAD_REQUEST, content=content
        )

    @staticmethod
    def redirect(url: str, status_code: int = status.HTTP_302_FOUND):
        """
        On redirect, returns RedirectResponse
        """
        return RedirectResponse(
            status_code=status_code,
            url=url,
        )


SameSite = Literal["lax", "strict", "none"]


class CookieOptions(TypedDict):
    """
    CookieOptions schema configuration
    """

    value: str
    max_age: NotRequired[int]
    httponly: NotRequired[bool]
    secure: NotRequired[bool]
    samesite: NotRequired[SameSite]


def get_cookie_response(
    cookies: dict[str, CookieOptions],
    response: JSONResponse | Response,
) -> JSONResponse | Response:
    """
    Sets cookies in the response applying secure settings for production/staging environments
    and development configurations for local testing.
    """
    for key, opts in cookies.items():
        value = opts["value"]

        if config.is_local or config.is_testing or config.is_development:
            response.set_cookie(
                key=key,
                value=value,
                httponly=opts.get("httponly", True),
                secure=opts.get("secure", False),
                samesite=opts.get("samesite", "lax"),
                max_age=opts.get("max_age"),
            )
        elif config.is_production or config.is_staging:
            response.set_cookie(
                key=key,
                value=value,
                httponly=opts.get("httponly", True),
                secure=opts.get("secure", True),
                samesite=opts.get("samesite", "none"),
                domain=config.COOKIE_DOMAIN,
                max_age=opts.get("max_age"),
            )

    return response
