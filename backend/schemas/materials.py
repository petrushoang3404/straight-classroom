from datetime import datetime
from pathlib import PurePath
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

MAX_FILE_SIZE = 50 * 1024 * 1024

# Mirrors the `accept` list on the upload form.
ALLOWED_CONTENT_TYPES = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
    }
)


def _basename(value: str) -> str:
    """Browsers send a bare name, but never trust a client with directories."""
    name = PurePath(value).name
    if not name:
        raise ValueError("Filename must not be empty")
    return name


def _supported_type(value: str) -> str:
    if value not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported file type: {value}")
    return value


Filename = Annotated[
    str, Field(min_length=1, max_length=255), AfterValidator(_basename)
]
ContentType = Annotated[str, Field(max_length=255), AfterValidator(_supported_type)]


class UploadUrlRequest(BaseModel):
    filename: Filename
    content_type: ContentType
    size_bytes: int = Field(gt=0, le=MAX_FILE_SIZE)


class UploadUrlResponse(BaseModel):
    object_key: str
    upload_url: str
    expires_in_seconds: int


class MaterialCreateRequest(BaseModel):
    """Sent once the browser has finished PUTting the file to `object_key`."""

    object_key: str = Field(min_length=1, max_length=1024)
    filename: Filename
    description: str | None = Field(default=None, max_length=1000)


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    classroom_id: int
    description: str | None
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime


class MaterialsResponse(BaseModel):
    items: list[MaterialResponse]
    limit: int
    offset: int
    total: int


class DownloadUrlResponse(BaseModel):
    download_url: str
    expires_in_seconds: int
