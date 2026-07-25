from pydantic import BaseModel


class IdentityHealthResponse(BaseModel):
    status: str
