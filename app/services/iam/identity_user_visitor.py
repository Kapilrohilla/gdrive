import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enum import IdentityProvider, UserStatus, VisitorAppType
from app.constants.permissions import STANDARD_ROLE_MEMBER
from app.models.iam.auth_events import AuthEventSubject
from app.schemas.endpoints.auth import LoginUserPayload, RegisterUserPayload
from app.services.iam.auth_event import AuthEventService
from app.services.iam.identity import IdentityService
from app.services.iam.rbac import RbacService
from app.services.iam.session import SessionService
from app.services.iam.visitors import VisitorService
from app.services.user import UserService
from app.services.utils.hashing import HashingService


class IdentityUserVisitorService:
    def __init__(
        self,
        identity_service: IdentityService,
        user_service: UserService,
        visitor_service: VisitorService,
        session_service: SessionService,
        auth_event_service: AuthEventService,
        rbac_service: RbacService | None = None,
    ):
        self.identity_service = identity_service
        self.user_service = user_service
        self.visitor_service = visitor_service
        self.session_service = session_service
        self.auth_event_service = auth_event_service
        self.rbac_service = rbac_service or RbacService()
        self.hashing_service = HashingService()

    async def register_user(
        self, visitor_id: uuid.UUID, payload: RegisterUserPayload, db: AsyncSession
    ):
        visitor = await self.visitor_service.get_visitor_by_id(visitor_id, db)
        if visitor is None:
            raise HTTPException(status_code=404, detail="Visitor not found")

        linked_user_id = await self.session_service.get_visitor_linked_user_id(visitor_id, db)
        if linked_user_id is not None:
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
        if payload.provider == IdentityProvider.LOCAL:
            secret_hash = self.hashing_service.hash(payload.password)

        role_id = await self._resolve_registration_role_id(visitor, payload.role_id, db)

        user = await self.user_service.create_user(
            db=db,
            full_name=payload.full_name,
            avatar=payload.avatar,
            role_id=role_id,
        )
        await db.flush()

        identity = await self.identity_service.create_identity(
            db=db,
            user_id=user.id,
            identifier=payload.identifier,
            identifier_type=payload.identifier_type,
            secret_hash=secret_hash,
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

    async def _resolve_registration_role_id(
        self,
        visitor,
        explicit_role_id: uuid.UUID | None,
        db: AsyncSession,
    ) -> uuid.UUID | None:
        if explicit_role_id is not None:
            return explicit_role_id

        app_type = visitor.app_type
        if isinstance(app_type, VisitorAppType):
            app_type_value = app_type.value
        else:
            app_type_value = str(app_type)

        if app_type_value != VisitorAppType.DRIVE_PORTAL.value:
            return None

        member_role = await self.rbac_service.get_role_by_name(STANDARD_ROLE_MEMBER, db)
        if member_role is None:
            raise HTTPException(
                status_code=500,
                detail="Member role is not configured",
            )

        return member_role.id

    async def login_user(self, visitor_id: uuid.UUID, payload: LoginUserPayload, db: AsyncSession):
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

        # disable the status check for now - reason need to build the verification process system first

        # if not self.identity_service.is_identity_active(identity):
        #     await self.auth_event_service.record(
        #         db=db,
        #         subject=AuthEventSubject.LOGIN_FAILED,
        #         success=False,
        #         user_id=identity.user_id,
        #         identity_id=identity.id,
        #         failure_reason="Identity is not active",
        #     )
        #     await db.commit()
        #     raise HTTPException(status_code=403, detail="Identity is not active")

        if payload.provider == IdentityProvider.LOCAL:
            if not self.identity_service.verify_local_credentials(identity, payload.password):
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

        linked_user_id = await self.session_service.get_visitor_linked_user_id(visitor_id, db)
        if linked_user_id is not None and linked_user_id != user.id:
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
