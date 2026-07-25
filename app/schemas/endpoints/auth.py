import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants.enum import (
    IdentifierType,
    IdentityProvider,
    IdentityStatus,
    UserStatus,
)
from app.schemas.iam.auth_event import AuthEventResponse


class RegisterUserPayload(BaseModel):
    provider: IdentityProvider = IdentityProvider.LOCAL
    identifier_type: IdentifierType
    identifier: str = Field(min_length=1, max_length=500)
    identifier_value: str | None = None
    full_name: str | None = None
    avatar: str | None = None
    role_id: uuid.UUID | None = None


class LoginUserPayload(BaseModel):
    provider: IdentityProvider = IdentityProvider.LOCAL
    identifier_type: IdentifierType
    identifier: str = Field(min_length=1, max_length=500)
    identifier_value: str = Field(min_length=1)


class AuthUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str | None
    avatar: str | None
    status: UserStatus
    role_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class AuthIdentityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    identifier: str
    identifier_type: IdentifierType
    status: IdentityStatus
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AuthVisitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    identifier_type: str
    identifier_value: str
    user_id: uuid.UUID | None
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expired_at: datetime
    refresh_token_expired_at: datetime
    user: AuthUserResponse
    identity: AuthIdentityResponse
    visitor: AuthVisitorResponse


class LogoutResponse(BaseModel):
    message: str


class LogoutAllResponse(BaseModel):
    message: str
    revoked_sessions: int


class AuthEventListResponse(BaseModel):
    events: list[AuthEventResponse]
