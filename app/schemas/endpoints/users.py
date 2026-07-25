from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)


class CreateUserResponse(BaseModel):
    message: str
    data: Any
    timestamp: datetime
