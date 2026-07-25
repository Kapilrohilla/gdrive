from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.constants.enum import TokenType
from app.middleware import authenticate
from app.schemas.endpoints.auth import (
    AuthTokenResponse,
    LoginUserPayload,
    RegisterUserPayload,
)
from app.services.iam.identity import IdentityService
from app.services.iam.identity_user_visitor import IdentityUserVisitorService
from app.services.iam.visitors import VisitorService
from app.services.user import UserService
from app.services.utils.jwt import JwtUtils

router = APIRouter(prefix="/auth", tags=["Auth"])

identity_service = IdentityService()
user_service = UserService()
visitor_service = VisitorService()
jwt_utils = JwtUtils()
identity_user_visitor_service = IdentityUserVisitorService(
    identity_service, user_service, visitor_service
)


@router.post(
    "/register/me",
    dependencies=[Depends(authenticate(TokenType.GUEST))],
    response_model=AuthTokenResponse,
)
async def register_me(
    request: Request, payload: RegisterUserPayload, db: AsyncSession = Depends(get_db)
):
    visitor_id = request.state.visitor_id

    user, identity, visitor = await identity_user_visitor_service.register_user(
        visitor_id=visitor_id, payload=payload, db=db
    )

    access_token, access_token_expired_at = jwt_utils.generate_token(
        token_type=TokenType.ACCESS,
        visitor_id=visitor.id,
        user_id=user.id,
        identity_id=identity.id,
    )
    refresh_token, refresh_token_expired_at = jwt_utils.generate_token(
        token_type=TokenType.REFRESH,
        visitor_id=visitor.id,
        user_id=user.id,
        identity_id=identity.id,
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


@router.post(
    "/login/me",
    dependencies=[Depends(authenticate(TokenType.GUEST))],
    response_model=AuthTokenResponse,
)
async def login_me(
    request: Request, payload: LoginUserPayload, db: AsyncSession = Depends(get_db)
):
    visitor_id = request.state.visitor_id

    user, identity, visitor = await identity_user_visitor_service.login_user(
        visitor_id=visitor_id, payload=payload, db=db
    )

    access_token, access_token_expired_at = jwt_utils.generate_token(
        token_type=TokenType.ACCESS,
        visitor_id=visitor.id,
        user_id=user.id,
        identity_id=identity.id,
    )
    refresh_token, refresh_token_expired_at = jwt_utils.generate_token(
        token_type=TokenType.REFRESH,
        visitor_id=visitor.id,
        user_id=user.id,
        identity_id=identity.id,
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
