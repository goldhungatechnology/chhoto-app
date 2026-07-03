from typing import Literal

from src.shared.infrastructure.uploader.adapter.cloudinary.cloudinary_uploader import (
    CloudinaryUploader,
)
from src.shared.infrastructure.uploader.adapter.s3.s3_uploader import S3Uploader
from src.shared.infrastructure.uploader.interface.uploader_interface import (
    UploaderInterface,
)


class BaseUploaderService:
    """Base uploader service that resolves uploader adapters."""

    def __init__(self, uploader: Literal["cloudinary", "s3"] = "cloudinary"):
        match uploader:
            case "cloudinary":
                self._uploader: UploaderInterface = CloudinaryUploader()
            case "s3":
                self._uploader = S3Uploader()
            case _:
                raise ValueError("Invalid uploader adapter")

    @property
    def client(self) -> UploaderInterface:
        return self._uploader
