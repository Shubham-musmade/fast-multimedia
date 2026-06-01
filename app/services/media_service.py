from fastapi import UploadFile
from app.repositories.media_repository import MediaRepository
from app.services.storage_service import StorageService
from app.services.validation_service import ValidationService
from app.models.media import MediaAsset

class MediaService:
    def __init__(self, repo: MediaRepository, storage: StorageService):
        self.repo = repo
        self.storage = storage

    async def upload(self, file: UploadFile, user_id: int) -> MediaAsset:
        # Validations
        ValidationService.validate_file_type(file)
        ValidationService.validate_file_size(file)
        await ValidationService.validate_daily_limit(self.repo, user_id)

        # Generate path
        storage_path = self.storage.generate_storage_path(user_id, file.filename)

        # Upload to GCS
        await self.storage.upload_file(file, storage_path)

        # Save metadata
        media = MediaAsset(
            user_id=user_id,
            original_filename=file.filename,
            file_type=file.filename.split(".")[-1].lower(),
            mime_type=file.content_type or "application/octet-stream",
            file_size=file.size or 0,
            storage_path=storage_path,
        )

        return await self.repo.create(media)