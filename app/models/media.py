from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # extension
    mime_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # bytes
    storage_path = Column(String(500), nullable=False, unique=True)
    upload_date = Column(DateTime, nullable=False, default=func.date(func.now()), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_media_user_upload_date", "user_id", "upload_date"),
    )