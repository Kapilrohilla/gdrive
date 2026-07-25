from fastapi import APIRouter

from app.schemas.endpoints.identity import IdentityHealthResponse

router = APIRouter(prefix="/identity", tags=["Identity"])


@router.get("/health", response_model=IdentityHealthResponse)
async def identity_health():
    return {"status": "ok"}
