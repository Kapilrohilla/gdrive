from fastapi import APIRouter, Depends

from app.constants.enum import TokenType
from app.middleware import authenticate
from app.schemas.endpoints.identity import IdentityHealthResponse

router = APIRouter(
    prefix="/identity",
    tags=["Identity"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)


@router.get("/health", response_model=IdentityHealthResponse)
async def identity_health():
    return {"status": "ok"}
