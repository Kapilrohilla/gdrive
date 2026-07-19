import uuid

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import Select, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Files, Folder
from app.models.file import FileStatus

s3_client = boto3.client(
    service_name="s3",
    aws_access_key_id=settings.aws_api_key,
    aws_secret_access_key=settings.aws_secret_key,
)


class FileService:
    @staticmethod
    async def generate_pre_signed_url(
        name: str,
        user_id: str,
        content_type: str,
        folder_id: str | None,
        db: AsyncSession,
    ):
        parent_folders = []
        parent_folder_ref = folder_id

        extension = name.split(".")[-1]

        if not extension:
            return {
                "is_valid": False,
                "message": "non extension file are not allowed",
            }

        while True:
            query = select(Folder).where(Folder.id == parent_folder_ref)
            query_response = await db.execute(query)
            parent_folder_detail = query_response.scalar()

            if parent_folder_detail is None:
                break

            parent_folders.append(
                {
                    "id": parent_folder_detail.id,
                    "name": parent_folder_detail.name,
                }
            )

            if parent_folder_detail.parent_id is None:
                break

            parent_folder_ref = parent_folder_detail.parent_id

        parent_folders.reverse()

        s3_key = ""
        if len(parent_folders) != 0:
            s3_key = f"users/{user_id}"
            for folder in parent_folders:
                s3_key += f"/{folder['name']}"
            s3_key += f"/{name}"

        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.aws_s3_bucket,
                "Key": s3_key,
                "ContentType": content_type,
            },
            ExpiresIn=3600,
        )

        file = Files(
            name=name,
            folder_id=folder_id,
            s3_path=s3_key,
            size=0,
            extension=extension,
        )

        db.add(file)
        await db.commit()

        return {
            "signed_url": url,
            "file_path": s3_key,
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
        try:
            s3_client.head_object(
                Bucket=settings.aws_s3_bucket,
                Key=data.s3_path,
            )
            exists = True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                exists = False
            else:
                raise

        stmt = update(Files).where(Files.id == id).values(status=FileStatus.READY)

        await db.execute(stmt)
        await db.commit()
        return {
            "is_valid": exists,
            "message": "uploaded" if exists else "Not uploaded",
        }

    async def get_files(self):
        pass

    async def get_file(self):
        pass

    async def save_url(self):
        pass


file_service = FileService()
