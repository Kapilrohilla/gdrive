from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate
from app.schemas.endpoints.auth import (
    AuthEventListResponse,
    AuthTokenResponse,
    LoginUserPayload,
    LogoutAllResponse,
    LogoutResponse,
    RegisterUserPayload,
)
from app.services.iam.auth_event import AuthEventService
from app.services.iam.auth_session import AuthSessionService
from app.services.iam.identity import IdentityService
from app.services.iam.identity_user_visitor import IdentityUserVisitorService
from app.services.iam.session import SessionService
from app.services.iam.visitors import VisitorService
from app.services.user import UserService
from app.services.utils.jwt import JwtUtils

router = APIRouter(prefix="/auth", tags=["Auth"])

identity_service = IdentityService()
user_service = UserService()
visitor_service = VisitorService()
session_service = SessionService()
auth_event_service = AuthEventService()
jwt_utils = JwtUtils()
auth_session_service = AuthSessionService(
    session_service,
    user_service,
    visitor_service,
    jwt_utils,
    auth_event_service,
)
identity_user_visitor_service = IdentityUserVisitorService(
    identity_service, user_service, visitor_service, auth_event_service
)


@router.post(
    "/register/me",
    dependencies=[Depends(authenticate(TokenType.GUEST))],
    response_model=AuthTokenResponse,
)
async def register_me(request: Request, payload: RegisterUserPayload, db: DbSession):
    visitor_id = UUID(str(request.state.visitor_id))

    user, identity, visitor = await identity_user_visitor_service.register_user(
        visitor_id=visitor_id, payload=payload, db=db
    )

    tokens = await auth_session_service.issue_tokens(
        db=db,
        user=user,
        identity=identity,
        visitor=visitor,
        request=request,
    )
    await db.commit()

    return tokens


@router.post(
    "/login/me",
    dependencies=[Depends(authenticate(TokenType.GUEST))],
    response_model=AuthTokenResponse,
)
async def login_me(request: Request, payload: LoginUserPayload, db: DbSession):
    visitor_id = UUID(str(request.state.visitor_id))

    user, identity, visitor = await identity_user_visitor_service.login_user(
        visitor_id=visitor_id, payload=payload, db=db
    )

    tokens = await auth_session_service.issue_tokens(
        db=db,
        user=user,
        identity=identity,
        visitor=visitor,
        request=request,
    )
    await db.commit()

    return tokens


@router.post(
    "/refresh",
    dependencies=[Depends(authenticate(TokenType.REFRESH))],
    response_model=AuthTokenResponse,
)
async def refresh_tokens(request: Request, db: DbSession):
    return await auth_session_service.refresh_tokens(
        db=db,
        session_id=UUID(str(request.state.session_id)),
        refresh_token=request.state.refresh_token,
        user_id=UUID(str(request.state.user_id)),
        identity_id=UUID(str(request.state.identity_id)),
        visitor_id=UUID(str(request.state.visitor_id)),
    )


@router.post(
    "/logout",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=LogoutResponse,
)
async def logout(request: Request, db: DbSession):
    await auth_session_service.logout(
        session_id=UUID(str(request.state.session_id)),
        db=db,
    )
    return {"message": "Logged out successfully"}


@router.post(
    "/logout/all",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=LogoutAllResponse,
)
async def logout_all_devices(request: Request, db: DbSession):
    revoked_sessions = await auth_session_service.logout_all_devices(
        user_id=UUID(str(request.state.user_id)),
        db=db,
    )
    return {
        "message": "Logged out from all devices successfully",
        "revoked_sessions": revoked_sessions,
    }


@router.get(
    "/events",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=AuthEventListResponse,
)
async def list_auth_events(request: Request, db: DbSession):
    events = await auth_session_service.list_auth_events(
        db=db,
        user_id=UUID(str(request.state.user_id)),
    )
    return {"events": events}
