from fastapi import UploadFile
from app.core.exceptions import InvalidFileType, FileTooLarge, UploadLimitExceeded
from app.core.config import settings
from app.repositories.media_repository import MediaRepository

class ValidationService:
    @staticmethod
    def validate_file_type(file: UploadFile):
        ext = file.filename.split(".")[-1].lower()
        if ext not in [e.lower() for e in settings.ALLOWED_EXTENSIONS]:
            raise InvalidFileType(f"File type .{ext} not allowed")
        if file.content_type not in settings.ALLOWED_MIME_TYPES:
            raise InvalidFileType("Invalid MIME type")

    @staticmethod
    def validate_file_size(file: UploadFile):
        if file.size and file.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise FileTooLarge(f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")

    @staticmethod
    async def validate_daily_limit(repo: MediaRepository, user_id: int):
        count = await repo.get_daily_upload_count(user_id)
        if count >= settings.DAILY_UPLOAD_LIMIT:
            raise UploadLimitExceeded(f"Daily upload limit of {settings.DAILY_UPLOAD_LIMIT} files exceeded")