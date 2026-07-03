from .base_uploader_service import BaseUploaderService

uploader = BaseUploaderService("cloudinary").client

__all__ = ["uploader"]
