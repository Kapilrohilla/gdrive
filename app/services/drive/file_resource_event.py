import uuid

from fastapi import HTTPException

from app.api.deps import DbSession
from app.constants.enum import ResourceEventResourceType
from app.services.drive.files import FileService
from app.services.resource_events import ResourceEventService


class FileResourceEventService:
    def __init__(self, file_service: FileService, resource_event_service: ResourceEventService):
        self.file_service = file_service
        self.resource_event_service = resource_event_service

    async def get_file_activity(self, db: DbSession, file_id: uuid.UUID) -> list[dict]:
        await self.file_service.get_file(db=db, id=file_id)

        resource_events = await self.resource_event_service.get_resource_events(
            db=db,
            resource_id=file_id,
            resource_type=ResourceEventResourceType.FILE,
        )

        return [
            {
                "action": resource_event.action,
                "timestamp": resource_event.created_at,
                "user_agent": resource_event.user_agent,
                "metadata": resource_event.event_metadata,
                "actor_id": resource_event.actor_id,
                "actor_type": resource_event.actor_type,
            }
            for resource_event in resource_events
        ]


__all__ = ["FileResourceEventService"]
