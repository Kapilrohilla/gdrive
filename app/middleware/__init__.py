from uuid import UUID

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.services.iam.session import SessionService
from app.services.iam.visitors import VisitorService
from app.services.utils.jwt import JwtUtils

jwt_utils = JwtUtils()
visitor_service = VisitorService()
session_service = SessionService()


def authenticate(token_type: TokenType):
    if token_type == TokenType.GUEST:
        return _authenticate_guest_dependency
    if token_type == TokenType.ACCESS:
        return _authenticate_access_dependency
    if token_type == TokenType.REFRESH:
        return _authenticate_refresh_dependency
    raise ValueError(f"Invalid token type: {token_type}")


def _extract_bearer_token(request: Request) -> str:
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    bearer_token = token.split(" ", 1)[1].strip()
    if not bearer_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return bearer_token


async def _touch_visitor_last_seen(
    visitor_id: UUID | str | None, db: AsyncSession
) -> None:
    if visitor_id is None:
        return
    await visitor_service.touch_last_seen_at(UUID(str(visitor_id)), db)


def _parse_uuid(value: UUID | str | None) -> UUID | None:
    if value is None:
        return None
    return UUID(str(value))


async def _authenticate_guest_dependency(request: Request, db: DbSession):
    try:
        token = _extract_bearer_token(request)
        payload = jwt_utils.verify_token(token_type=TokenType.GUEST, token=token)
        request.state.visitor_id = payload.get("visitor_id")
        await _touch_visitor_last_seen(request.state.visitor_id, db)
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def _authenticate_access_dependency(request: Request, db: DbSession):
    try:
        token = _extract_bearer_token(request)
        payload = jwt_utils.verify_token(token_type=TokenType.ACCESS, token=token)
        session_id = _parse_uuid(payload.get("session_id"))
        if session_id is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        session = await session_service.get_active_session(session_id, db)
        if session is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        request.state.user_id = payload.get("user_id")
        request.state.identity_id = payload.get("identity_id")
        request.state.visitor_id = payload.get("visitor_id")
        request.state.session_id = session_id
        await session_service.touch_session(session_id, db)
        await _touch_visitor_last_seen(request.state.visitor_id, db)
        await db.commit()
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def _authenticate_refresh_dependency(request: Request, db: DbSession):
    try:
        token = _extract_bearer_token(request)
        payload = jwt_utils.verify_token(token_type=TokenType.REFRESH, token=token)
        session_id = _parse_uuid(payload.get("session_id"))
        if session_id is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        session = await session_service.get_active_session(session_id, db)
        if session is None:
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
