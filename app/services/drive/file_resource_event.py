import uuid

from app.api.deps import DbSession
from app.constants.enum import ResourceEventResourceType
from app.services.drive.files import FileService
from app.services.resource_events import ResourceEventService


def _serialize_resource_event(resource_event) -> dict:
    return {
        "action": resource_event.action,
        "timestamp": resource_event.created_at,
        "user_agent": resource_event.user_agent,
        "metadata": resource_event.event_metadata,
        "actor_id": resource_event.actor_id,
        "actor_type": resource_event.actor_type,
        "resource_id": resource_event.resource_id,
    }


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

        return [_serialize_resource_event(resource_event) for resource_event in resource_events]

    async def get_my_file_activity(self, db: DbSession, user_id: uuid.UUID) -> list[dict]:
        resource_events = await self.resource_event_service.get_my_resource_events(
            db=db,
            actor_id=user_id,
            resource_type=ResourceEventResourceType.FILE,
        )
        return [_serialize_resource_event(resource_event) for resource_event in resource_events]


__all__ = ["FileResourceEventService"]
