import secrets
import uuid

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enum import TokenType
from app.models.iam.auth_events import AuthEvent, AuthEventSubject
from app.models.iam.identity import Identity
from app.models.iam.user import User
from app.models.iam.visitor import Visitor
from app.services.iam.auth_event import AuthEventService
from app.services.iam.session import SessionService
from app.services.iam.visitors import VisitorService
from app.services.user import UserService
from app.services.utils.jwt import JwtUtils


class AuthSessionService:
    def __init__(
        self,
        session_service: SessionService,
        user_service: UserService,
        visitor_service: VisitorService,
        jwt_utils: JwtUtils,
        auth_event_service: AuthEventService,
    ):
        self.session_service = session_service
        self.user_service = user_service
        self.visitor_service = visitor_service
        self.jwt_utils = jwt_utils
        self.auth_event_service = auth_event_service

    async def issue_tokens(
        self,
        db: AsyncSession,
        user: User,
        identity: Identity,
        visitor: Visitor,
        request: Request | None = None,
    ) -> dict:
        provisional_refresh = secrets.token_urlsafe(48)
        refresh_expires_at = SessionService.default_refresh_expiry()

        session = await self.session_service.create_session(
            db=db,
            user_id=user.id,
            identity_id=identity.id,
            refresh_token=provisional_refresh,
            expires_at=refresh_expires_at,
            user_agent=request.headers.get("user-agent") if request else None,
            ip=request.client.host if request and request.client else None,
        )

        access_token, access_token_expired_at = self.jwt_utils.generate_token(
            token_type=TokenType.ACCESS,
            visitor_id=visitor.id,
            user_id=user.id,
            identity_id=identity.id,
            session_id=session.id,
        )
        refresh_token, refresh_token_expired_at = self.jwt_utils.generate_token(
            token_type=TokenType.REFRESH,
            visitor_id=visitor.id,
            user_id=user.id,
            identity_id=identity.id,
            session_id=session.id,
        )
        await self.session_service.rotate_refresh_token(
            session=session,
            refresh_token=refresh_token,
            expires_at=refresh_token_expired_at,
            db=db,
        )
        await self.auth_event_service.record(
            db=db,
            subject=AuthEventSubject.SESSION_CREATED,
            success=True,
            user_id=user.id,
            identity_id=identity.id,
            session_id=session.id,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_token_expired_at": access_token_expired_at,
            "refresh_token_expired_at": refresh_token_expired_at,
            "user": user,
            "identity": identity,
            "visitor": visitor,
        }

    async def refresh_tokens(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        refresh_token: str,
        user_id: uuid.UUID,
        identity_id: uuid.UUID,
        visitor_id: uuid.UUID,
    ) -> dict:
        try:
            session = await self.session_service.validate_refresh_session(
                session_id=session_id,
                refresh_token=refresh_token,
                db=db,
            )
        except ValueError as exc:
            await self.auth_event_service.record(
                db=db,
                subject=AuthEventSubject.SESSION_REVOKED,
                success=False,
                user_id=user_id,
                identity_id=identity_id,
                session_id=session_id,
                failure_reason="Invalid refresh token",
            )
            await db.commit()
            raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

        if session.user_id != user_id or session.identity_id != identity_id:
            await self.auth_event_service.record(
                db=db,
                subject=AuthEventSubject.SESSION_REVOKED,
                success=False,
                user_id=user_id,
                identity_id=identity_id,
                session_id=session_id,
                failure_reason="Token claims mismatch",
            )
            await db.commit()
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = await self.user_service.get_user_by_id(user_id, db)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        visitor = await self.visitor_service.get_visitor_by_id(visitor_id, db)
        if visitor is None:
            raise HTTPException(status_code=404, detail="Visitor not found")

        access_token, access_token_expired_at = self.jwt_utils.generate_token(
            token_type=TokenType.ACCESS,
            visitor_id=visitor_id,
            user_id=user_id,
            identity_id=identity_id,
            session_id=session.id,
        )
        new_refresh_token, refresh_token_expired_at = self.jwt_utils.generate_token(
            token_type=TokenType.REFRESH,
            visitor_id=visitor_id,
            user_id=user_id,
            identity_id=identity_id,
            session_id=session.id,
        )
        await self.session_service.rotate_refresh_token(
            session=session,
            refresh_token=new_refresh_token,
            expires_at=refresh_token_expired_at,
            db=db,
        )
        await db.commit()
        await db.refresh(user)
        await db.refresh(session)
        await db.refresh(visitor)

        identity = await db.get(Identity, identity_id)
        if identity is None:
            raise HTTPException(status_code=404, detail="Identity not found")

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "access_token_expired_at": access_token_expired_at,
            "refresh_token_expired_at": refresh_token_expired_at,
            "user": user,
            "identity": identity,
            "visitor": visitor,
        }

    async def logout(self, session_id: uuid.UUID, db: AsyncSession) -> None:
        session = await self.session_service.get_session_by_id(session_id, db)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

        await self.session_service.revoke_session(session_id, db)
        await self.auth_event_service.record(
            db=db,
            subject=AuthEventSubject.LOGOUT,
            success=True,
            user_id=session.user_id,
            identity_id=session.identity_id,
            session_id=session.id,
        )
        await self.auth_event_service.record(
            db=db,
            subject=AuthEventSubject.SESSION_REVOKED,
            success=True,
            user_id=session.user_id,
            identity_id=session.identity_id,
            session_id=session.id,
        )
        await db.commit()

    async def logout_all_devices(self, user_id: uuid.UUID, db: AsyncSession) -> int:
        revoked_count = await self.session_service.revoke_all_user_sessions(
            user_id=user_id,
            db=db,
        )
        await self.auth_event_service.record(
            db=db,
            subject=AuthEventSubject.LOGOUT,
            success=True,
            user_id=user_id,
            failure_reason=f"revoked_sessions={revoked_count}",
        )
        await self.auth_event_service.record(
            db=db,
            subject=AuthEventSubject.SESSION_REVOKED,
            success=True,
            user_id=user_id,
            failure_reason=f"revoked_sessions={revoked_count}",
        )
        await db.commit()
        return revoked_count

    async def list_auth_events(
        self,
        db: AsyncSession,
        user_id: uuid.UUID | None = None,
        limit: int = 100,
    ):
        stmt = select(AuthEvent).order_by(AuthEvent.created_at.desc()).limit(limit)
        if user_id is not None:
            stmt = stmt.where(AuthEvent.user_id == user_id)

        result = await db.execute(stmt)
        return list(result.scalars().all())
