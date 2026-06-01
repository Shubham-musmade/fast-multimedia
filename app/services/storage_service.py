from google.cloud import storage
from fastapi import UploadFile
from app.core.config import settings
from datetime import datetime
import os

class StorageService:
    def __init__(self):
        self.client = storage.Client(project=settings.GCS_PROJECT_ID)
        self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)

    def generate_storage_path(self, user_id: int, filename: str) -> str:
        now = datetime.utcnow()
        ext = filename.split(".")[-1].lower()
        safe_filename = f"{datetime.utcnow().strftime('%H%M%S')}_{filename.replace(' ', '_')}"

        return f"media/{now.year:04d}/{now.month:02d}/{now.day:02d}/user_{user_id}/uploads/{safe_filename}"

    async def upload_file(self, file: UploadFile, storage_path: str) -> str:
        blob = self.bucket.blob(storage_path)

        # Stream upload (memory efficient)
        content = await file.read()
        blob.upload_from_string(content, content_type=file.content_type)

        return storage_path

    async def delete_file(self, storage_path: str):
        blob = self.bucket.blob(storage_path)
        if blob.exists():
            blob.delete()