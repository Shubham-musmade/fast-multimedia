from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.media import MediaAsset
from datetime import date

class MediaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, media: MediaAsset) -> MediaAsset:
        self.db.add(media)
        await self.db.commit()
        await self.db.refresh(media)
        return media

    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 20, search: str | None = None, file_type: str | None = None):
        query = select(MediaAsset).where(MediaAsset.user_id == user_id)

        if search:
            query = query.where(MediaAsset.original_filename.ilike(f"%{search}%"))
        if file_type:
            query = query.where(MediaAsset.file_type == file_type)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        query = query.order_by(MediaAsset.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_by_id_and_user(self, media_id: int, user_id: int) -> MediaAsset | None:
        query = select(MediaAsset).where(
            MediaAsset.id == media_id,
            MediaAsset.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, media: MediaAsset):
        await self.db.delete(media)
        await self.db.commit()

    async def get_daily_upload_count(self, user_id: int) -> int:
        today = date.today()
        query = select(func.count()).select_from(MediaAsset).where(
            MediaAsset.user_id == user_id,
            func.date(MediaAsset.upload_date) == today
        )
        result = await self.db.execute(query)
        return result.scalar() or 0