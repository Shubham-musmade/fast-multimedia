from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.media_service import MediaService
from app.services.storage_service import StorageService
from app.repositories.media_repository import MediaRepository
from app.schemas.media import MediaAssetResponse, MediaListResponse
from fastapi import HTTPException
from app.core.logging import log

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/upload", response_model=MediaAssetResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = MediaRepository(db)
    storage = StorageService()
    service = MediaService(repo, storage)

    try:
        media = await service.upload(file, current_user["user_id"], current_user["user_email"])
    except Exception as e:
        log.error(f"Upload failed: {e}")
        raise HTTPException(status_code=502, detail=f"Storage error: {str(e)}")
    print('media: ', media)
    return MediaAssetResponse(
        id=media.id,
        uuid=media.uuid,
        filename=media.original_filename,
        file_size=media.file_size,
        storage_path=media.storage_path,
        created_at=media.created_at
    )

@router.get("/", response_model=MediaListResponse)
async def list_media(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    file_type: str | None = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        repo = MediaRepository(db)
        skip = (page - 1) * size
        items, total = await repo.get_by_user(
            user_id=current_user["user_id"],
            skip=skip,
            limit=size,
            search=search,
            file_type=file_type
        )
        print(
            [
                MediaAssetResponse(
                    id=item.id,
                    uuid=item.uuid,
                    filename=getattr(item, "original_filename", None),
                    file_size=item.file_size,
                    storage_path=item.storage_path,
                    # storage_path=str(StorageService().generate_signed_url(item.storage_path)) if item.storage_path else None,
                    created_at=item.created_at,
                )
                for item in items
            ]
        )
        return MediaListResponse(
            items=[
                MediaAssetResponse(
                    id=item.id,
                    uuid=item.uuid,
                    filename=getattr(item, "original_filename", None),
                    file_size=item.file_size,
                    storage_path=item.storage_path,
                    created_at=item.created_at,
                )
                for item in items
            ],
            total=total,
            page=page,
            size=size,
        )
    except Exception as e:
        log.error(f"Failed to list media: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve media list")

@router.get("/{media_id}", response_model=MediaAssetResponse)
async def get_media(
    media_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = MediaRepository(db)
    media = await repo.get_by_id_and_user(media_id, current_user["user_id"])
    if not media:
        raise FileNotFound()
    return MediaAssetResponse.model_validate(media)

@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = MediaRepository(db)
    storage = StorageService()
    media = await repo.get_by_id_and_user(media_id, current_user["user_id"])
    if not media:
        raise FileNotFound()

    await storage.delete_file(media.storage_path)
    await repo.delete(media)
    return {"status": "deleted"}