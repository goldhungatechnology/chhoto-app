from src.core.config.settings import config

from .base_uploader_service import BaseUploaderService

uploader = BaseUploaderService(config.UPLOAD_PROVIDER).client

__all__ = ["uploader"]
