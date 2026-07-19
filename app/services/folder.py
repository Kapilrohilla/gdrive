import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.folder import Folder


class FolderService:
    async def create_folder(
        self,
        name: str,
        owner_id: str,
        parent_id: str | None,
        db: AsyncSession,
    ):
        folder = Folder(
            name=name,
            owner_id=uuid.UUID(owner_id),
            parent_id=uuid.UUID(parent_id) if parent_id else None,
        )
        db.add(folder)
        await db.commit()
        await db.refresh(folder)
        return folder

    async def get_folder(
        self,
        owner_id: str | None,
        parent_id: str | None,
        db: AsyncSession,
    ):
        query = select(Folder)

        if owner_id is not None:
            query = query.where(Folder.owner_id == uuid.UUID(owner_id))
        if parent_id is not None:
            query = query.where(Folder.parent_id == uuid.UUID(parent_id))

        result = await db.execute(query)
        return result.scalars().all()


folder_service = FolderService()
