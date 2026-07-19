import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class AuthEventSubject(str, Enum):
    LOGIN_SUCCESS = "login success"
    LOGIN_FAILED = "login failed"
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password changed"
    PASSWORD_RESET = "password reset"
    EMAIL_VERIFIED = "email verified"
    OTP_SENT = "otp sent"
    OTP_VERIFIED = "otp verified"
    SESSION_CREATED = "session created"
    SESSION_REVOKED = "session revoked"
    ACCOUNT_LOCKED = "account locked"


class AuthEventBase(BaseModel):
    subject: AuthEventSubject
    success: bool
    user_id: uuid.UUID | None = None
    identity_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None
    failure_reason: str | None = None


class CreateAuthEventDto(AuthEventBase):
    pass


class AuthEventResponse(AuthEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
