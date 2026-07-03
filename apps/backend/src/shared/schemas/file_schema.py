from src.shared.schemas import BaseSchema


class UploadedFileResponse(BaseSchema):
    filename: str | None = None
    original_filename: str | None = None
    content_type: str | None = None
    size: int | None = None
    url: str
    provider: str | None = None

    model_config = {"from_attributes": True, "extra": "ignore"}
