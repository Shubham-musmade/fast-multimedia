from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class MediaAssetResponse(BaseModel):
    id: int
    uuid: str
    filename: str
    file_size: int
    storage_path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MediaListResponse(BaseModel):
    items: list[MediaAssetResponse]
    total: int
    page: int
    size: int