from google.cloud import storage
from google.oauth2 import service_account
from fastapi import UploadFile
from app.core.config import settings
from datetime import datetime
import os
from app.core.logging import log


class StorageService:
    def __init__(self):
        # Prefer explicit service account file if provided via settings
        try:
            if settings.GCS_CREDENTIALS_FILE:
                if not os.path.exists(settings.GCS_CREDENTIALS_FILE):
                    raise FileNotFoundError(f"GCS credentials file not found: {settings.GCS_CREDENTIALS_FILE}")
                creds = service_account.Credentials.from_service_account_file(settings.GCS_CREDENTIALS_FILE)
                self.client = storage.Client(project=settings.GCS_PROJECT_ID, credentials=creds)
            else:
                # Fall back to Application Default Credentials
                self.client = storage.Client(project=settings.GCS_PROJECT_ID)
            self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)
        except Exception as e:
            log.error(f"Failed to initialize GCS client: {e}")
            raise

    def generate_storage_path(self, filename: str, user_id: int, user_email: str = "Anonymous") -> str:
        now = datetime.utcnow()
        ext = filename.split(".")[-1].lower()
        safe_filename = f"{datetime.utcnow().strftime('%H%M%S')}_{filename.replace(' ', '_')}"

        return f"media/{now.year:04d}/{now.month:02d}/{now.day:02d}/user_{user_email if user_email else user_id}/uploads/{safe_filename}"

    async def upload_file(self, file: UploadFile, storage_path: str) -> str:
        blob = self.bucket.blob(storage_path)

        # Stream upload (memory efficient)
        content = await file.read()
        try:
            blob.upload_from_string(content, content_type=file.content_type)
        except Exception as e:
            log.error(f"Failed to upload to GCS: {e}")
            raise

        return storage_path

    async def delete_file(self, storage_path: str):
        blob = self.bucket.blob(storage_path)
        try:
            if blob.exists():
                blob.delete()
        except Exception as e:
            log.error(f"Failed to delete from GCS: {e}")
            raise
    
    # Media retrieval (e.g., generating signed URLs) can be added here if needed
    async def get_file_url(self, storage_path: str) -> str:
        blob = self.bucket.blob(storage_path)
        if not blob.exists():
            raise FileNotFoundError("File not found in storage")
        return blob.public_url
    async def generate_signed_url(self, storage_path: str, expiration_minutes: int = 15) -> str:
        blob = self.bucket.blob(storage_path)
        print('blob: ', blob)
        if not blob.exists():
            raise FileNotFoundError("File not found in storage")
        try:
            url = blob.generate_signed_url(expiration=expiration_minutes * 60)
            print('Generated signed URL: ', url)
            return url
        except Exception as e:
            log.error(f"Failed to generate signed URL: {e}")
            raise