import datetime
import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drive.files import Files, FileStatus
from app.models.drive.folder import Folder


def serialize_folder(folder: Folder, item_count: int | None = None) -> dict:
    return {
        "id": folder.id,
        "name": folder.name,
        "parent_id": folder.parent_id,
        "owner_id": folder.owner_id,
        "file_count": item_count if item_count is not None else folder.file_count,
        "created_at": folder.created_at,
        "updated_at": folder.updated_at,
        "is_trashed": folder.is_trashed,
        "trashed_at": folder.trashed_at,
    }


class FolderService:
    async def create_folder(
        self,
        name: str,
        owner_id: uuid.UUID,
        parent_id: uuid.UUID | None,
        db: AsyncSession,
    ) -> Folder:
        if parent_id is not None:
            parent = await db.get(Folder, parent_id)
            if parent is None or parent.is_trashed:
                raise HTTPException(status_code=404, detail="Parent folder not found")
            if parent.owner_id != owner_id:
                raise HTTPException(status_code=403, detail="Parent folder access denied")

        stmt = select(Folder).where(
            Folder.name == name,
            Folder.owner_id == owner_id,
            Folder.parent_id == parent_id,
            Folder.is_trashed.is_(False),
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=400, detail="Folder with same name already exists")

        folder = Folder(
            name=name,
            owner_id=owner_id,
            parent_id=parent_id,
        )
        db.add(folder)
        await db.flush()
        return folder

    async def get_folders(
        self,
        owner_id: uuid.UUID,
        parent_id: uuid.UUID | None,
        db: AsyncSession,
    ) -> list[dict]:
        query = (
            select(Folder)
            .where(
                Folder.owner_id == owner_id,
                Folder.parent_id == parent_id,
                Folder.is_trashed.is_(False),
            )
            .order_by(Folder.created_at.desc())
        )
        result = await db.execute(query)
        folders = result.scalars().all()

        serialized: list[dict] = []
        for folder in folders:
            item_count = await self._count_folder_items(folder.id, db)
            serialized.append(serialize_folder(folder, item_count=item_count))
        return serialized

    async def get_trashed_folders(self, owner_id: uuid.UUID, db: AsyncSession) -> list[dict]:
        query = (
            select(Folder)
            .where(
                Folder.owner_id == owner_id,
                Folder.is_trashed.is_(True),
            )
            .order_by(Folder.trashed_at.desc())
        )
        result = await db.execute(query)
        return [serialize_folder(folder) for folder in result.scalars().all()]

    async def get_folder(
        self,
        folder_id: uuid.UUID,
        owner_id: uuid.UUID,
        db: AsyncSession,
        *,
        include_trashed: bool = False,
    ) -> Folder:
        folder = await db.get(Folder, folder_id)
        if folder is None:
            raise HTTPException(status_code=404, detail="Folder not found")
        if folder.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Folder access denied")
        if folder.is_trashed and not include_trashed:
            raise HTTPException(status_code=404, detail="Folder not found")
        return folder

    async def rename_folder(
        self,
        folder_id: uuid.UUID,
        name: str,
        owner_id: uuid.UUID,
        db: AsyncSession,
    ) -> Folder:
        folder = await self.get_folder(folder_id, owner_id, db)
        folder.name = name
        db.add(folder)
        await db.commit()
        await db.refresh(folder)
        return folder

    async def trash_folder(
        self,
        folder_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> Folder:
        folder = await self.get_folder(folder_id, user_id, db, include_trashed=True)
        if folder.is_trashed:
            raise HTTPException(status_code=400, detail="Folder is already in trash")

        folder.is_trashed = True
        folder.trashed_at = datetime.datetime.now(datetime.UTC)
        folder.trashed_by_id = user_id
        db.add(folder)
        await db.commit()
        await db.refresh(folder)
        return folder

    async def restore_folder(
        self,
        folder_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> Folder:
        folder = await self.get_folder(folder_id, user_id, db, include_trashed=True)
        if not folder.is_trashed:
            raise HTTPException(status_code=400, detail="Folder is not in trash")

        folder.is_trashed = False
        folder.trashed_at = None
        folder.trashed_by_id = None
        db.add(folder)
        await db.commit()
        await db.refresh(folder)
        return folder

    async def empty_trash(self, owner_id: uuid.UUID, db: AsyncSession) -> int:
        query = select(Folder).where(
            Folder.owner_id == owner_id,
            Folder.is_trashed.is_(True),
        )
        result = await db.execute(query)
        folders = list(result.scalars().all())

        for folder in folders:
            await db.delete(folder)

        if folders:
            await db.commit()

        return len(folders)

    async def _count_folder_items(self, folder_id: uuid.UUID, db: AsyncSession) -> int:
        file_count_stmt = (
            select(func.count())
            .select_from(Files)
            .where(
                Files.folder_id == str(folder_id),
                Files.status == FileStatus.READY,
                Files.is_trashed.is_(False),
            )
        )
        subfolder_count_stmt = (
            select(func.count())
            .select_from(Folder)
            .where(
                Folder.parent_id == folder_id,
                Folder.is_trashed.is_(False),
            )
        )

        file_count = await db.scalar(file_count_stmt) or 0
        subfolder_count = await db.scalar(subfolder_count_stmt) or 0
        return file_count + subfolder_count


__all__ = ["FolderService", "serialize_folder"]
