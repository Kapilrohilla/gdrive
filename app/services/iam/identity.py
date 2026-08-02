import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enum import IdentifierType, IdentityStatus
from app.models.iam.identity import Identity
from app.services.utils.hashing import HashingService


class IdentityService:
    def __init__(self):
        self.hashing_service = HashingService()

    async def get_identity_by_identifier(
        self,
        identifier: str,
        identifier_type: IdentifierType,
        db: AsyncSession,
    ) -> Identity | None:
        stmt = select(Identity).where(
            Identity.identifier == identifier.lower(),
            Identity.identifier_type == identifier_type,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_identity(
        self,
        db: AsyncSession,
        user_id,
        identifier: str,
        identifier_type: IdentifierType,
        secret_hash: str | None = None,
    ) -> Identity:
        identity = Identity(
            user_id=user_id,
            identifier=identifier.lower(),
            identifier_type=identifier_type,
            secret_hash=secret_hash,
        )
        db.add(identity)
        await db.flush()
        return identity

    async def record_successful_login(self, identity: Identity, db: AsyncSession) -> Identity:
        identity.last_login_at = datetime.now(timezone.utc)
        identity.consecutive_failed_count = 0
        db.add(identity)
        await db.flush()
        return identity

    async def record_failed_login(self, identity: Identity, db: AsyncSession) -> None:
        identity.consecutive_failed_count += 1
        db.add(identity)
        await db.flush()

    def verify_local_credentials(self, identity: Identity, password: str) -> bool:
        if identity.secret_hash is None:
            return False
        return self.hashing_service.verify(password, identity.secret_hash)

    def is_identity_active(self, identity: Identity) -> bool:
        return identity.status == IdentityStatus.ACTIVE

    async def get_identity_by_id(self, identity_id: uuid.UUID, db: AsyncSession) -> Identity | None:
        stmt = select(Identity).where(Identity.id == identity_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
