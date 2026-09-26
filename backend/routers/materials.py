"""Classroom materials.

Uploads are a three-step handshake so file bytes never touch this API:

1. ``POST .../materials/upload-url`` hands the browser a presigned PUT URL
   together with the object key it will be stored under.
2. The browser PUTs the file straight to MinIO.
3. ``POST .../materials`` registers the finished upload and returns the row.

Downloads work the same way, via a short-lived presigned GET URL.
"""

from typing import Annotated

from backend import storage
from backend.repository.errors import NotFoundError
from backend.repository.materials import MaterialRepo
from backend.schemas.materials import (
    ALLOWED_CONTENT_TYPES,
    MAX_FILE_SIZE,
    DownloadUrlResponse,
    MaterialCreateRequest,
    MaterialResponse,
    MaterialsResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)
from backend.security import require_classroom_access
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

router = APIRouter(
    prefix="/classrooms/{classroom_id}/materials",
    tags=["materials"],
    dependencies=[Depends(require_classroom_access)],
)

EXPIRES_IN_SECONDS = int(storage.PRESIGNED_URL_TTL.total_seconds())

MATERIAL_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Material not found",
)


@router.get("", response_model=MaterialsResponse)
def get_materials(
    classroom_id: Annotated[int, Path(gt=0)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repo: MaterialRepo = Depends(MaterialRepo),
):
    try:
        rows, total = repo.list(classroom_id, limit=limit, offset=offset)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return MaterialsResponse(items=rows, limit=limit, offset=offset, total=total)


@router.post("/upload-url", response_model=UploadUrlResponse)
def create_upload_url(
    classroom_id: Annotated[int, Path(gt=0)],
    upload: UploadUrlRequest,
):
    object_key = storage.build_object_key(classroom_id, upload.filename)
    return UploadUrlResponse(
        object_key=object_key,
        upload_url=storage.presigned_put_url(object_key),
        expires_in_seconds=EXPIRES_IN_SECONDS,
    )


@router.post(
    "",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_material(
    classroom_id: Annotated[int, Path(gt=0)],
    material: MaterialCreateRequest,
    repo: MaterialRepo = Depends(MaterialRepo),
):
    if not material.object_key.startswith(storage.classroom_prefix(classroom_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Object key does not belong to this classroom",
        )

    # Size and content type come from the stored object rather than the
    # request, so a client can't register something other than what it sent.
    stat = storage.stat_object(material.object_key)
    if stat is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload was not completed",
        )
    if stat.size > MAX_FILE_SIZE:
        storage.remove_object(material.object_key)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File exceeds the 50 MB limit",
        )
    if stat.content_type not in ALLOWED_CONTENT_TYPES:
        # Only set if the browser sent Content-Type on the PUT, which it must.
        storage.remove_object(material.object_key)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {stat.content_type}",
        )

    return repo.create(
        material.model_dump()
        | {
            "classroom_id": classroom_id,
            "content_type": stat.content_type,
            "size_bytes": stat.size,
        }
    )


@router.get("/{material_id}/download-url", response_model=DownloadUrlResponse)
def create_download_url(
    classroom_id: Annotated[int, Path(gt=0)],
    material_id: Annotated[int, Path(gt=0)],
    repo: MaterialRepo = Depends(MaterialRepo),
):
    material = repo.get_by_id(classroom_id, material_id)
    if material is None:
        raise MATERIAL_NOT_FOUND
    return DownloadUrlResponse(
        download_url=storage.presigned_get_url(
            material.object_key, filename=material.filename
        ),
        expires_in_seconds=EXPIRES_IN_SECONDS,
    )


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    classroom_id: Annotated[int, Path(gt=0)],
    material_id: Annotated[int, Path(gt=0)],
    repo: MaterialRepo = Depends(MaterialRepo),
):
    material = repo.get_by_id(classroom_id, material_id)
    if material is None:
        raise MATERIAL_NOT_FOUND

    object_key = material.object_key
    repo.delete(material)
    # Dropping the row first: a leftover object is harmless, a row pointing at
    # a deleted object is not.
    storage.remove_object(object_key)
