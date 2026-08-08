import datetime
import uuid

import boto3
from boto3.session import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException
from sqlalchemy import Select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.config import settings
from app.constants.enum import (
    AggregateType,
    OutboxTopics,
    ResourceEventActions,
    ResourceEventResourceType,
)
from app.models import Files
from app.models.drive.files import FileStatus
from app.services.utils.outbox import OutboxMessage, OutboxService

s3_client = boto3.client(
    service_name="s3",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_api_key,
    aws_secret_access_key=settings.aws_secret_key,
    config=Config(s3={"addressing_style": "virtual"}),
)

outbox_service = OutboxService()


def serialize_file(file: Files) -> dict:
    return {
        "id": file.id,
        "name": file.name,
        "folder_id": file.folder_id,
        "owner_id": file.owner_id,
        "storage_path": file.storage_path,
        "size": file.size,
        "extension": file.extension,
        "status": file.status,
        "last_accessed_at": file.last_accessed_at,
        "created_at": file.created_at,
        "is_trashed": file.is_trashed,
        "trashed_at": file.trashed_at,
    }


class FileService:
    @staticmethod
    async def initialize_upload(
        name: str,
        user_id: str,
        content_type: str,
        folder_id: str | None,
        db: AsyncSession,
    ):
        extension = name.split(".")[-1]

        if not extension or extension == name:
            return {
                "is_valid": False,
                "message": "non extension file are not allowed",
            }

        file = Files(
            name=name,
            folder_id=folder_id,
            owner_id=uuid.UUID(user_id),
            storage_path="",
            size=0,
            extension=extension,
        )
        db.add(file)
        await db.flush()

        prefix = folder_id if folder_id is not None else user_id
        storage_path = f"{prefix}/{file.id}.{extension}"

        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.aws_s3_bucket,
                "Key": storage_path,
                # "ContentType": content_type,
            },
            ExpiresIn=3600,
        )

        file.storage_path = storage_path
        await db.commit()

        return {
            "signed_url": url,
            "file_path": storage_path,
            "file_id": file.id,
            "method": "PUT",
            "headers": {
                "Content-Type": content_type,
            },
        }

    @staticmethod
    async def complete_upload(id: uuid.UUID, db: AsyncSession):
        query = Select(Files).where(Files.id == id)
        query_response = await db.execute(query)
        try:
            data = query_response.scalar_one()
        except NoResultFound:
            return {
                "is_valid": False,
                "message": "record not found in db",
            }

        exists = False
        file_size = data.size
        try:
            response = s3_client.head_object(
                Bucket=settings.aws_s3_bucket,
                Key=data.storage_path,
            )
            exists = True
            file_size = response.get("ContentLength", data.size)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                exists = False
            else:
                raise

        if not exists:
            return {
                "is_valid": False,
                "message": "Not uploaded",
            }

        stmt = (
            update(Files)
            .where(Files.id == id)
            .values(
                status=FileStatus.READY,
                size=file_size,
            )
        )
        await db.execute(stmt)

        await outbox_service.send_message(
            db=db,
            message=OutboxMessage(
                topic=OutboxTopics.GENERATE_FILE_THUMBNAIL,
                aggregate_type=AggregateType.FILE,
                aggregate_id=str(data.id),
                payload={
                    "id": str(data.id),
                    "storage_path": data.storage_path,
                    "size": file_size,
                    "extension": data.extension,
                },
            ),
        )
        await db.commit()

        return {
            "is_valid": True,
            "message": "uploaded",
        }

    async def get_files(
        self,
        db: DbSession,
        owner_id: uuid.UUID,
        folder_id: uuid.UUID | None = None,
    ) -> list[Files]:
        query = (
            Select(Files)
            .where(
                Files.status == FileStatus.READY,
                Files.is_trashed.is_(False),
                Files.owner_id == owner_id,
            )
            .order_by(Files.created_at.desc())
        )
        if folder_id is None:
            query = query.where(Files.folder_id.is_(None))
        else:
            query = query.where(Files.folder_id == str(folder_id))
        query_response = await db.execute(query)
        return list(query_response.scalars().all())

    async def get_recent_files(
        self,
        db: DbSession,
        owner_id: uuid.UUID,
        limit: int = 20,
    ) -> list[Files]:
        query = (
            Select(Files)
            .where(
                Files.status == FileStatus.READY,
                Files.is_trashed.is_(False),
                Files.owner_id == owner_id,
            )
            .order_by(Files.last_accessed_at.desc())
            .limit(limit)
        )
        query_response = await db.execute(query)
        return list(query_response.scalars().all())

    async def get_trashed_files(self, db: DbSession, owner_id: uuid.UUID) -> list[Files]:
        query = (
            Select(Files)
            .where(
                Files.is_trashed.is_(True),
                Files.owner_id == owner_id,
            )
            .order_by(Files.trashed_at.desc())
        )
        query_response = await db.execute(query)
        return list(query_response.scalars().all())

    async def get_file(
        self, db: DbSession, id: uuid.UUID, *, include_trashed: bool = False
    ) -> Files:
        query = Select(Files).where(Files.id == id)
        if not include_trashed:
            query = query.where(Files.is_trashed.is_(False))
        query_response = await db.execute(query)
        try:
            return query_response.scalar_one()
        except NoResultFound as exc:
            raise HTTPException(status_code=404, detail="File not found") from exc

    async def rename_file(
        self, db: DbSession, id: uuid.UUID, name: str, owner_id: uuid.UUID
    ) -> Files:
        file = await self.get_file(db, id)
        if file.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="File access denied")

        extension = name.rsplit(".", 1)[-1] if "." in name else ""
        if not extension or extension == name:
            raise HTTPException(status_code=400, detail="File name must include an extension")

        file.name = name
        file.extension = extension
        db.add(file)
        await db.commit()
        await db.refresh(file)
        return file

    async def trash_file(self, db: DbSession, id: uuid.UUID, user_id: uuid.UUID) -> Files:
        file = await self.get_file(db, id, include_trashed=True)
        if file.owner_id != user_id:
            raise HTTPException(status_code=403, detail="File access denied")
        if file.is_trashed:
            raise HTTPException(status_code=400, detail="File is already in trash")

        file.is_trashed = True
        file.trashed_at = datetime.datetime.now()
        file.trashed_by_id = user_id
        db.add(file)
        await db.commit()
        await db.refresh(file)
        return file

    async def restore_file(self, db: DbSession, id: uuid.UUID, user_id: uuid.UUID) -> Files:
        file = await self.get_file(db, id, include_trashed=True)
        if file.owner_id != user_id:
            raise HTTPException(status_code=403, detail="File access denied")
        if not file.is_trashed:
            raise HTTPException(status_code=400, detail="File is not in trash")

        file.is_trashed = False
        file.trashed_at = None
        file.trashed_by_id = None
        db.add(file)
        await db.commit()
        await db.refresh(file)
        return file

    async def empty_trash(self, db: DbSession, owner_id: uuid.UUID) -> int:
        files = await self.get_trashed_files(db, owner_id)
        deleted_count = 0

        for file in files:
            if file.storage_path:
                try:
                    s3_client.delete_object(
                        Bucket=settings.aws_s3_bucket,
                        Key=file.storage_path,
                    )
                except ClientError:
                    pass

            if file.thumbnail_path:
                try:
                    s3_client.delete_object(
                        Bucket=settings.aws_s3_bucket,
                        Key=file.thumbnail_path,
                    )
                except ClientError:
                    pass

            await db.delete(file)
            deleted_count += 1

        if deleted_count:
            await db.commit()

        return deleted_count

    async def _generate_presigned_get_url(
        self,
        file: Files,
        *,
        disposition: str,
    ) -> str:
        return s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.aws_s3_bucket,
                "Key": file.storage_path,
                "ResponseContentDisposition": f'{disposition}; filename="{file.name}"',
            },
            ExpiresIn=5 * 60,
        )

    async def _record_file_access(
        self,
        db: DbSession,
        file: Files,
        *,
        action: ResourceEventActions,
        url: str,
        user_agent: str | None,
        actor_id: uuid.UUID | None = None,
    ) -> None:
        file.last_accessed_at = datetime.datetime.now()
        db.add(file)

        await outbox_service.send_message(
            db=db,
            message=OutboxMessage(
                topic=OutboxTopics.CREATE_RESOURCE_EVENT,
                aggregate_type=AggregateType.FILE,
                aggregate_id=str(file.id),
                payload={
                    "action": action,
                    "resource_id": str(file.id),
                    "resource_type": ResourceEventResourceType.FILE,
                    "actor_id": str(actor_id) if actor_id is not None else None,
                    "metadata": {
                        "url": url,
                        "file_id": str(file.id),
                        "file_name": file.name,
                        "file_extension": file.extension,
                        "file_size": file.size,
                    },
                    "user_agent": user_agent,
                },
            ),
        )
        await db.commit()

    async def preview_file_url(
        self,
        db: DbSession,
        id: uuid.UUID,
        user_agent: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> dict:
        file = await self.get_file(db, id)

        if file.status != FileStatus.READY:
            return {
                "is_valid": False,
                "message": "file is not ready",
            }

        url = await self._generate_presigned_get_url(file, disposition="inline")
        await self._record_file_access(
            db,
            file,
            action=ResourceEventActions.VIEWED,
            url=url,
            user_agent=user_agent,
            actor_id=actor_id,
        )
        return {
            "url": url,
            **serialize_file(file),
        }

    async def download_file_url(
        self,
        db: DbSession,
        id: uuid.UUID,
        user_agent: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> dict:
        file = await self.get_file(db, id)

        if file.status != FileStatus.READY:
            return {
                "is_valid": False,
                "message": "file is not ready",
            }

        url = await self._generate_presigned_get_url(file, disposition="attachment")
        await self._record_file_access(
            db,
            file,
            action=ResourceEventActions.DOWNLOADED,
            url=url,
            user_agent=user_agent,
            actor_id=actor_id,
        )

        return {
            "url": url,
            **serialize_file(file),
        }


__all__ = ["FileService", "serialize_file"]
