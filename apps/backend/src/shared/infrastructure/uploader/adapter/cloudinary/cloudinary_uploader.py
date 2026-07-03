from typing import Any

import httpx

from src.core.config.settings import config
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.logger import logger
from src.shared.infrastructure.uploader.interface.uploader_interface import (
    UploaderInterface,
)


class CloudinaryUploader(UploaderInterface):
    """Cloudinary uploader adapter using Cloudinary Upload API."""

    async def upload_files(
        self, files: list[tuple[str, bytes, str | None]]
    ) -> list[dict[str, Any]]:
        cloud_name = config.CLOUDINARY_CLOUD_NAME
        api_key = config.CLOUDINARY_API_KEY
        api_secret = config.CLOUDINARY_API_SECRET

        if not cloud_name or not api_key or not api_secret:
            raise ServerError(error="Cloudinary configuration is missing")

        upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/auto/upload"
        auth = (api_key, api_secret)
        results: list[dict[str, Any]] = []
        timeout = httpx.Timeout(connect=10.0, read=60.0, write=60.0, pool=10.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            for filename, content, content_type in files:
                multipart_file = (
                    "file",
                    (filename, content, content_type or "application/octet-stream"),
                )
                data = {"folder": config.CLOUDINARY_FOLDER}

                try:
                    response = await client.post(
                        upload_url, auth=auth, data=data, files=[multipart_file]
                    )
                    response.raise_for_status()
                except httpx.TimeoutException as e:
                    logger.error(
                        f"[Uploader] Cloudinary upload timed out for {filename}: {e!s}"
                    )
                    raise ServerError(
                        error="Cloudinary upload timed out. Please try again.",
                        internal_details=str(e),
                    ) from e
                except httpx.HTTPStatusError as e:
                    logger.error(
                        f"[Uploader] Cloudinary upload failed for {filename}: {e.response.text}"
                    )
                    raise ServerError(
                        error="Failed to upload file to Cloudinary",
                        internal_details=str(e),
                    ) from e
                except httpx.RequestError as e:
                    logger.error(
                        f"[Uploader] Cloudinary request failed for {filename}: {e!s}"
                    )
                    raise ServerError(
                        error="Failed to connect to Cloudinary",
                        internal_details=str(e),
                    ) from e

                try:
                    payload = response.json()
                except ValueError as e:
                    logger.error(
                        f"[Uploader] Invalid Cloudinary response for {filename}: {response.text}"
                    )
                    raise ServerError(
                        error="Invalid response from Cloudinary",
                        internal_details=str(e),
                    ) from e
                secure_url = payload.get("secure_url")
                if not isinstance(secure_url, str) or not secure_url:
                    raise ServerError(error="Cloudinary response missing secure_url")

                results.append(
                    {
                        "filename": payload.get("public_id"),
                        "original_filename": payload.get("original_filename")
                        or filename,
                        "content_type": content_type,
                        "size": payload.get("bytes"),
                        "url": secure_url,
                        "provider": "cloudinary",
                    }
                )

        return results
