"""MinIO (S3-compatible) object storage for classroom materials.

Clients upload and download through presigned URLs, so file bytes go straight
between the browser and MinIO and never pass through this API.
"""

from datetime import timedelta
from pathlib import PurePath
from urllib.parse import quote
from uuid import uuid4

from minio import Minio
from minio.datatypes import Object
from minio.error import S3Error

from backend.config import settings

PRESIGNED_URL_TTL = timedelta(minutes=15)

client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=settings.minio_secure,
)


def ensure_bucket() -> None:
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)


def classroom_prefix(classroom_id: int) -> str:
    return f"classrooms/{classroom_id}/"


def build_object_key(classroom_id: int, filename: str) -> str:
    """A key nobody can guess, namespaced by classroom.

    The random segment keeps two uploads of the same file apart and stops a
    client from handing back a key that points at somebody else's object.
    """
    suffix = PurePath(filename).suffix.lower()
    return f"{classroom_prefix(classroom_id)}{uuid4().hex}{suffix}"


def presigned_put_url(object_key: str) -> str:
    return client.presigned_put_object(
        settings.minio_bucket, object_key, expires=PRESIGNED_URL_TTL
    )


def presigned_get_url(object_key: str, *, filename: str) -> str:
    """Download URL that saves the file under its original name.

    RFC 5987 encoding keeps non-ASCII names (Vietnamese titles, typically)
    intact and leaves nothing to escape in the header.
    """
    return client.presigned_get_object(
        settings.minio_bucket,
        object_key,
        expires=PRESIGNED_URL_TTL,
        response_headers={
            "response-content-disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
        },
    )


def stat_object(object_key: str) -> Object | None:
    """Metadata of an uploaded object, or None if the upload never landed."""
    try:
        return client.stat_object(settings.minio_bucket, object_key)
    except S3Error:
        return None


def remove_object(object_key: str) -> None:
    client.remove_object(settings.minio_bucket, object_key)
