import uuid

from sqlalchemy import Select

from app.api.deps import DbSession
from app.constants.enum import ResourceEventActions, ResourceEventActorType, ResourceEventResourceType
from app.models.resource_events import ResourceEvents


class ResourceEventService:
    async def get_resource_events(
        self,
        db: DbSession,
        resource_id: uuid.UUID,
        resource_type: ResourceEventResourceType,
    ) -> list[ResourceEvents]:
        query = Select(ResourceEvents).where(
            ResourceEvents.resource_id == str(resource_id),
            ResourceEvents.resource_type == resource_type,
        )
        query_response = await db.execute(query)
        return list(query_response.scalars().all())

    async def create_resource_event(
        self,
        db: DbSession,
        resource_id: uuid.UUID,
        resource_type: ResourceEventResourceType,
        action: ResourceEventActions,
        metadata: dict,
        user_agent: str | None = None,
        actor_id: uuid.UUID | None = None,
        actor_type: ResourceEventActorType | None = None,
    ) -> ResourceEvents:
        resource_event = ResourceEvents(
            resource_id=str(resource_id),
            resource_type=resource_type,
            action=action,
            event_metadata=metadata,
            user_agent=user_agent,
            actor_id=actor_id,
            actor_type=actor_type or ResourceEventActorType.SYSTEM,
        )
        db.add(resource_event)
        await db.flush()
        return resource_event


__all__ = ["ResourceEventService"]
