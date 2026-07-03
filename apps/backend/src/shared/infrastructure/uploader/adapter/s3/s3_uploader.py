import uuid
from typing import Any, cast

import aioboto3
from botocore.exceptions import BotoCoreError, ClientError

from src.core.config.settings import config
from src.shared.exceptions.base_exceptions import ServerError
from src.shared.infrastructure.logger import logger
from src.shared.infrastructure.uploader.interface.uploader_interface import (
    UploaderInterface,
)


class S3Uploader(UploaderInterface):
    """AWS S3 uploader adapter using aioboto3."""

    async def upload_files(
        self, files: list[tuple[str, bytes, str | None]]
    ) -> list[dict[str, Any]]:
        bucket = config.AWS_S3_BUCKET
        region = config.AWS_S3_REGION
        access_key = config.AWS_ACCESS_KEY_ID
        secret_key = config.AWS_SECRET_ACCESS_KEY

        if not bucket or not region or not access_key or not secret_key:
            raise ServerError(error="S3 configuration is missing")

        folder = config.AWS_S3_FOLDER.strip("/")
        endpoint_url = config.AWS_S3_ENDPOINT_URL
        public_base_url = config.AWS_S3_PUBLIC_BASE_URL

        results: list[dict[str, Any]] = []
        session = aioboto3.Session()

        s3_client_cm = cast(
            Any,
            session.client(
                "s3",
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                endpoint_url=endpoint_url,
            ),
        )
        async with s3_client_cm as client:
            for filename, content, content_type in files:
                key = (
                    f"{folder}/{uuid.uuid4().hex}-{filename}"
                    if folder
                    else f"{uuid.uuid4().hex}-{filename}"
                )
                resolved_content_type = content_type or "application/octet-stream"

                try:
                    await client.put_object(
                        Bucket=bucket,
                        Key=key,
                        Body=content,
                        ContentType=resolved_content_type,
                    )
                except (BotoCoreError, ClientError) as e:
                    logger.error(f"[Uploader] S3 upload failed for {filename}: {e!s}")
                    raise ServerError(
                        error="Failed to upload file to S3", internal_details=str(e)
                    ) from e

                if public_base_url:
                    url = f"{public_base_url.rstrip('/')}/{key}"
                elif endpoint_url:
                    url = f"{endpoint_url.rstrip('/')}/{bucket}/{key}"
                else:
                    url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

                results.append(
                    {
                        "filename": key,
                        "original_filename": filename,
                        "content_type": resolved_content_type,
                        "size": len(content),
                        "url": url,
                        "provider": "s3",
                    }
                )

        return results
