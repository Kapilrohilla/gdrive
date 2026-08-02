from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.constants.enum import UserStatus


class CreateUserRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)


class CreateUserResponse(BaseModel):
    message: str
    data: object
    timestamp: datetime


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    full_name: str | None
    email: str
    avatar: str | None
    status: UserStatus


class GetUserProfileResponse(BaseModel):
    message: str
    data: UserProfileResponse
    timestamp: datetime