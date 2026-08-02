from uuid import UUID

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.services.iam.identity import IdentityService
from app.services.iam.session import SessionService
from app.services.iam.visitors import VisitorService
from app.services.user import UserService
from app.services.utils.jwt import JwtUtils

jwt_utils = JwtUtils()
visitor_service = VisitorService()
session_service = SessionService()
user_service = UserService()
identity_service = IdentityService()


def _extract_bearer_token(request: Request) -> str:
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    bearer_token = token.split(" ", 1)[1].strip()
    if not bearer_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return bearer_token


async def _touch_visitor_last_seen(visitor_id: UUID | str | None, db: AsyncSession) -> None:
    if visitor_id is None:
        return
    await visitor_service.touch_last_seen_at(UUID(str(visitor_id)), db)


def _parse_uuid(value: UUID | str | None) -> UUID | None:
    if value is None:
        return None
    return UUID(str(value))


async def authenticate_guest_dependency(request: Request, db: DbSession):
    try:
        token = _extract_bearer_token(request)
        payload = jwt_utils.verify_token(token_type=TokenType.GUEST, token=token)
        request.state.visitor_id = payload.get("visitor_id")
        await _touch_visitor_last_seen(request.state.visitor_id, db)
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def authenticate_access_dependency(request: Request, db: DbSession):
    try:
        token = _extract_bearer_token(request)
        payload = jwt_utils.verify_token(token_type=TokenType.ACCESS, token=token)
        session_id = _parse_uuid(payload.get("session_id"))
        if session_id is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        session = await session_service.get_active_session(session_id, db)
        if session is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        payload_visitor_id = _parse_uuid(payload.get("visitor_id"))
        if payload_visitor_id is None or session.visitor_id != payload_visitor_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        request.state.user_id = payload.get("user_id")
        request.state.identity_id = payload.get("identity_id")
        request.state.visitor_id = payload.get("visitor_id")
        request.state.session_id = session_id
        # fetch the visitor, identity, user from database
        visitor = await visitor_service.get_visitor_by_id(UUID(payload.get("visitor_id")), db)
        identity = await identity_service.get_identity_by_id(UUID(payload.get("identity_id")), db)
        user = await user_service.get_user_by_id(UUID(payload.get("user_id")), db)
        request.state.visitor = visitor
        request.state.identity = identity
        request.state.user = user
        await session_service.touch_session(session_id, db)
        await _touch_visitor_last_seen(request.state.visitor_id, db)
        await db.commit()
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def authenticate_refresh_dependency(request: Request, db: DbSession):
    try:
        token = _extract_bearer_token(request)
        payload = jwt_utils.verify_token(token_type=TokenType.REFRESH, token=token)
        session_id = _parse_uuid(payload.get("session_id"))
        if session_id is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        session = await session_service.get_active_session(session_id, db)
        if session is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        payload_visitor_id = _parse_uuid(payload.get("visitor_id"))
        if payload_visitor_id is None or session.visitor_id != payload_visitor_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        request.state.user_id = payload.get("user_id")
        request.state.identity_id = payload.get("identity_id")
        request.state.visitor_id = payload.get("visitor_id")
        request.state.session_id = session_id
        request.state.refresh_token = token
        await _touch_visitor_last_seen(request.state.visitor_id, db)
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")
