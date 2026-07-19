from pydantic import BaseModel


class CreateUserDto(BaseModel):
    full_name: str
