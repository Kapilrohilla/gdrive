import datetime
import uuid

import boto3
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
    aws_access_key_id=settings.aws_api_key,
    aws_secret_access_key=settings.aws_secret_key,
)

outbox_service = OutboxService()


def serialize_file(file: Files) -> dict:
    return {
        "id": file.id,
        "name": file.name,
        "folder_id": file.folder_id,
        "storage_path": file.storage_path,
        "size": file.size,
        "extension": file.extension,
        "status": file.status,
        "last_accessed_at": file.last_accessed_at,
        "created_at": file.created_at,
    }


class FileService:
    @staticmethod
    async def generate_pre_signed_url(
        name: str,
        user_id: str,
        content_type: str,
        folder_id: str | None,
        db: AsyncSession,
    ):
        extension = name.split(".")[-1]

        if not extension:
            return {
                "is_valid": False,
                "message": "non extension file are not allowed",
            }

        storage_path = folder_id if folder_id is not None else user_id

        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.aws_s3_bucket,
                "Key": storage_path,
                "ContentType": content_type,
            },
            ExpiresIn=3600,
        )

        file = Files(
            name=name,
            folder_id=folder_id,
            storage_path=storage_path,
            size=0,
            extension=extension,
        )

        db.add(file)
        await db.commit()

        return {
            "signed_url": url,
            "file_path": storage_path,
            "file_id": file.id,
        }

    @staticmethod
    async def mark_upload_complete(id: uuid.UUID, db: AsyncSession):
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

        stmt = update(Files).where(Files.id == id).values(
            status=FileStatus.READY,
            size=file_size,
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
        self, db: DbSession, folder_id: uuid.UUID | None = None
    ) -> list[Files]:
        query = (
            Select(Files)
            .where(Files.status == FileStatus.READY)
            .order_by(Files.created_at.desc())
        )
        if folder_id is None:
            query = query.where(Files.folder_id.is_(None))
        else:
            query = query.where(Files.folder_id == str(folder_id))
        query_response = await db.execute(query)
        return list(query_response.scalars().all())

    async def get_file(self, db: DbSession, id: uuid.UUID) -> Files:
        query = Select(Files).where(Files.id == id)
        query_response = await db.execute(query)
        try:
            return query_response.scalar_one()
        except NoResultFound as exc:
            raise HTTPException(status_code=404, detail="File not found") from exc

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
        file.last_accessed_at = datetime.datetime.now(datetime.UTC)
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
