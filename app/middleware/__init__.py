from uuid import UUID

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.constants.enum import TokenType
from app.services.iam.visitors import VisitorService
from app.services.utils.jwt import JwtUtils

jwt_utils = JwtUtils()
visitor_service = VisitorService()


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


async def _authenticate_guest_dependency(
    request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        token = _extract_bearer_token(request)
        payload = jwt_utils.verify_token(token_type=TokenType.GUEST, token=token)
        request.state.visitor_id = payload.get("visitor_id")
        await _touch_visitor_last_seen(request.state.visitor_id, db)
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def _authenticate_access_dependency(
    request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        token = _extract_bearer_token(request)
        payload = jwt_utils.verify_token(token_type=TokenType.ACCESS, token=token)
        request.state.user_id = payload.get("user_id")
        request.state.identity_id = payload.get("identity_id")
        request.state.visitor_id = payload.get("visitor_id")
        await _touch_visitor_last_seen(request.state.visitor_id, db)
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def _authenticate_refresh_dependency(
    request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        token = _extract_bearer_token(request)
        payload = jwt_utils.verify_token(token_type=TokenType.REFRESH, token=token)
        request.state.user_id = payload.get("user_id")
        request.state.identity_id = payload.get("identity_id")
        request.state.visitor_id = payload.get("visitor_id")
        await _touch_visitor_last_seen(request.state.visitor_id, db)
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=401, detail="Unauthorized")
