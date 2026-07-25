import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enum import IdentityProvider, UserStatus
from app.models.iam.auth_events import AuthEventSubject
from app.schemas.endpoints.auth import LoginUserPayload, RegisterUserPayload
from app.services.iam.auth_event import AuthEventService
from app.services.iam.identity import IdentityService
from app.services.iam.visitors import VisitorService
from app.services.user import UserService


class IdentityUserVisitorService:
    def __init__(
        self,
        identity_service: IdentityService,
        user_service: UserService,
        visitor_service: VisitorService,
        auth_event_service: AuthEventService,
    ):
        self.identity_service = identity_service
        self.user_service = user_service
        self.visitor_service = visitor_service
        self.auth_event_service = auth_event_service

    async def register_user(
        self, visitor_id: uuid.UUID, payload: RegisterUserPayload, db: AsyncSession
    ):
        visitor = await self.visitor_service.get_visitor_by_id(visitor_id, db)
        if visitor is None:
            raise HTTPException(status_code=404, detail="Visitor not found")

        if visitor.user_id is not None:
            raise HTTPException(
                status_code=409,
                detail="Visitor is already linked to a user",
            )

        identity = await self.identity_service.get_identity_by_identifier(
            identifier=payload.identifier,
            identifier_type=payload.identifier_type,
            db=db,
        )
        if identity is not None:
            raise HTTPException(
                status_code=409,
                detail="Identity already registered",
            )

        secret_hash = None
        if payload.provider == IdentityProvider.LOCAL and payload.identifier_value:
            secret_hash = payload.identifier_value

        user = await self.user_service.create_user(
            db=db,
            full_name=payload.full_name,
            avatar=payload.avatar,
            role_id=payload.role_id,
        )
        await db.flush()

        identity = await self.identity_service.create_identity(
            db=db,
            user_id=user.id,
            identifier=payload.identifier,
            identifier_type=payload.identifier_type,
            secret_hash=secret_hash,
        )
        await self.visitor_service.link_visitor_to_user(
            visitor_id=visitor_id,
            user_id=user.id,
            db=db,
        )

        await self.auth_event_service.record(
            db=db,
            subject=AuthEventSubject.LOGIN_SUCCESS,
            success=True,
            user_id=user.id,
            identity_id=identity.id,
            failure_reason="registration",
        )

        await db.commit()
        await db.refresh(user)
        await db.refresh(identity)
        await db.refresh(visitor)

        return user, identity, visitor

    async def login_user(
        self, visitor_id: uuid.UUID, payload: LoginUserPayload, db: AsyncSession
    ):
        visitor = await self.visitor_service.get_visitor_by_id(visitor_id, db)
        if visitor is None:
            raise HTTPException(status_code=404, detail="Visitor not found")

        identity = await self.identity_service.get_identity_by_identifier(
            identifier=payload.identifier,
            identifier_type=payload.identifier_type,
            db=db,
        )
        if identity is None:
            await self.auth_event_service.record(
                db=db,
                subject=AuthEventSubject.LOGIN_FAILED,
                success=False,
                failure_reason="Invalid credentials",
            )
            await db.commit()
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not self.identity_service.is_identity_active(identity):
            await self.auth_event_service.record(
                db=db,
                subject=AuthEventSubject.LOGIN_FAILED,
                success=False,
                user_id=identity.user_id,
                identity_id=identity.id,
                failure_reason="Identity is not active",
            )
            await db.commit()
            raise HTTPException(status_code=403, detail="Identity is not active")

        if payload.provider == IdentityProvider.LOCAL:
            if not self.identity_service.verify_local_credentials(
                identity, payload.identifier_value
            ):
                await self.identity_service.record_failed_login(identity, db)
                await self.auth_event_service.record(
                    db=db,
                    subject=AuthEventSubject.LOGIN_FAILED,
                    success=False,
                    user_id=identity.user_id,
                    identity_id=identity.id,
                    failure_reason="Invalid credentials",
                )
                await db.commit()
                raise HTTPException(status_code=401, detail="Invalid credentials")

        user = await self.user_service.get_user_by_id(identity.user_id, db)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user.status != UserStatus.ACTIVE:
            await self.auth_event_service.record(
                db=db,
                subject=AuthEventSubject.LOGIN_FAILED,
                success=False,
                user_id=user.id,
                identity_id=identity.id,
                failure_reason="User is not active",
            )
            await db.commit()
            raise HTTPException(status_code=403, detail="User is not active")

        if visitor.user_id is None:
            await self.visitor_service.link_visitor_to_user(
                visitor_id=visitor_id,
                user_id=user.id,
                db=db,
            )
        elif visitor.user_id != user.id:
            await self.auth_event_service.record(
                db=db,
                subject=AuthEventSubject.LOGIN_FAILED,
                success=False,
                user_id=user.id,
                identity_id=identity.id,
                failure_reason="Visitor linked to a different user",
            )
            await db.commit()
            raise HTTPException(
                status_code=409,
                detail="Visitor is linked to a different user",
            )

        await self.identity_service.record_successful_login(identity, db)
        await self.auth_event_service.record(
            db=db,
            subject=AuthEventSubject.LOGIN_SUCCESS,
            success=True,
            user_id=user.id,
            identity_id=identity.id,
        )

        await db.commit()
        await db.refresh(user)
        await db.refresh(identity)
        await db.refresh(visitor)

        return user, identity, visitor
