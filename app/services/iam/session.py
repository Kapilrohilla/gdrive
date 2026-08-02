import uuid
from datetime import datetime, timedelta, timezone

from app.core.security import hash_refresh_token, verify_refresh_token
from app.models.iam.session import Session
from app.services.utils.jwt import REFRESH_EXPIRY_DAYS
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SessionService:
    async def create_session(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        identity_id: uuid.UUID,
        visitor_id: uuid.UUID,
        refresh_token: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip: str | None = None,
    ) -> Session:
        session = Session(
            user_id=user_id,
            identity_id=identity_id,
            visitor_id=visitor_id,
            refresh_token_hash=hash_refresh_token(refresh_token),
            user_agent=user_agent,
            ip=ip,
            expires_at=expires_at,
            last_seen_at=datetime.now(timezone.utc),
        )
        db.add(session)
        await db.flush()
        return session

    async def get_session_by_id(self, session_id: uuid.UUID, db: AsyncSession) -> Session | None:
        stmt = select(Session).where(Session.id == session_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_session(self, session_id: uuid.UUID, db: AsyncSession) -> Session | None:
        session = await self.get_session_by_id(session_id, db)
        if session is None:
            return None
        if not self._is_session_active(session):
            return None
        return session

    async def validate_refresh_session(
        self,
        session_id: uuid.UUID,
        refresh_token: str,
        db: AsyncSession,
    ) -> Session:
        session = await self.get_session_by_id(session_id, db)
        if session is None or not self._is_session_active(session):
            raise ValueError("Invalid session")
        if not verify_refresh_token(refresh_token, session.refresh_token_hash):
            raise ValueError("Invalid refresh token")
        return session

    async def rotate_refresh_token(
        self,
        session: Session,
        refresh_token: str,
        expires_at: datetime,
        db: AsyncSession,
    ) -> Session:
        session.refresh_token_hash = hash_refresh_token(refresh_token)
        session.expires_at = expires_at
        session.last_seen_at = datetime.now(timezone.utc)
        session.revoked_at = None
        db.add(session)
        await db.flush()
        return session

    async def touch_session(self, session_id: uuid.UUID, db: AsyncSession) -> None:
        stmt = (
            update(Session)
            .where(Session.id == session_id, Session.revoked_at.is_(None))
            .values(last_seen_at=datetime.now(timezone.utc))
        )
        await db.execute(stmt)

    async def revoke_session(self, session_id: uuid.UUID, db: AsyncSession) -> Session | None:
        session = await self.get_session_by_id(session_id, db)
        if session is None or session.revoked_at is not None:
            return session

        session.revoked_at = datetime.now(timezone.utc)
        db.add(session)
        await db.flush()
        return session

    async def revoke_all_user_sessions(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
        exclude_session_id: uuid.UUID | None = None,
    ) -> int:
        stmt = select(Session).where(
            Session.user_id == user_id,
            Session.revoked_at.is_(None),
        )
        if exclude_session_id is not None:
            stmt = stmt.where(Session.id != exclude_session_id)

        result = await db.execute(stmt)
        sessions = result.scalars().all()
        revoked_at = datetime.now(timezone.utc)

        for session in sessions:
            session.revoked_at = revoked_at
            db.add(session)

        await db.flush()
        return len(sessions)

    def _is_session_active(self, session: Session) -> bool:
        if session.revoked_at is not None:
            return False
        return not (
            session.expires_at is not None and session.expires_at <= datetime.now(timezone.utc)
        )

    async def get_visitor_linked_user_id(
        self, visitor_id: uuid.UUID, db: AsyncSession
    ) -> uuid.UUID | None:
        stmt = (
            select(Session.user_id)
            .where(Session.visitor_id == visitor_id)
            .order_by(Session.created_at.asc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def default_refresh_expiry() -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRY_DAYS)
