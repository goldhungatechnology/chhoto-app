from typing import Any, Literal, NotRequired, TypedDict

from fastapi import Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from starlette.status import HTTP_204_NO_CONTENT

from src.core.config.settings import config


class CustomSuccessResponseSchema[T](BaseModel):
    """
    Custom Error Response Schema for every api
    """

    success: bool
    data: T | list[T] | None
    message: str


class CustomErrorResponseSchema[T](BaseModel):
    """
    Custom Error Response Schema for every api
    """

    success: bool
    errors: T | list[T] | None
    error: str


class CustomResponse:
    """
    list of customer Response methods
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Successful",
        status_code: int = status.HTTP_200_OK,
    ):
        """
        On sucess it returns the success=True with data and message
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
        On error it returns the success=False and with data and message
        """
        content = {"success": False, "error": error, "errors": jsonable_encoder(errors)}
        return JSONResponse(
            status_code=status_code or status.HTTP_400_BAD_REQUEST, content=content
        )

    @staticmethod
    def redirect(url: str, status_code: int = status.HTTP_302_FOUND):
        """
        On redirect it returns the success=True with data and message
        """
        return RedirectResponse(
            status_code=status_code,
            url=url,
        )


SameSite = Literal["lax", "strict", "none"]


class CookieOptions(TypedDict):
    """
    CookieOptions is a TypedDict that defines the structure of the options for setting cookies in HTTP responses. It includes the following fields:
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
    custom cookie response handler that sets cookies in the response based on the provided options and environment configuration. It iterates through the cookies dictionary, applying different settings for local and production environments to ensure secure cookie handling in production while allowing more flexibility during local development.
    """

    for key, opts in cookies.items():
        value = opts["value"]

        print("Cookie domain", config.COOKIE_DOMAIN)

        # environment defaults
        if config.is_local or config.is_testing or config.is_development:
            response.set_cookie(
                key=key,
                value=value,
                # Always HttpOnly so the session cookie is never readable from
                # JS (XSS theft). `secure` stays optional in non-prod because
                # local dev is served over plain http.
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
