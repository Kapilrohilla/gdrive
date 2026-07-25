import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.iam.auth_events import AuthEvent, AuthEventSubject


class AuthEventService:
    async def record(
        self,
        db: AsyncSession,
        subject: AuthEventSubject,
        success: bool,
        user_id: uuid.UUID | None = None,
        identity_id: uuid.UUID | None = None,
        session_id: uuid.UUID | None = None,
        failure_reason: str | None = None,
    ) -> AuthEvent:
        event = AuthEvent(
            subject=subject,
            success=success,
            user_id=user_id,
            identity_id=identity_id,
            session_id=session_id,
            failure_reason=failure_reason,
        )
        db.add(event)
        await db.flush()
        return event
