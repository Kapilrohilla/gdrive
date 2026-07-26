from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate, require_permission
from app.models.iam.permission import PermissionAction
from app.schemas.endpoints.visitor import (
    RegisterVisitorRequest,
    RegisterVisitorResponse,
)
from app.services.iam.visitor_jwt import VisitorJwtService
from app.services.iam.visitors import VisitorService
from app.services.utils.jwt import JwtUtils

router = APIRouter(prefix="/visitor", tags=["Visitor"])

visitor_service = VisitorService()
jwt_utils = JwtUtils()
visitor_jwt_service = VisitorJwtService(visitor_service=visitor_service, jwt_utils=jwt_utils)


@router.get(
    "/",
    dependencies=[
        Depends(authenticate(TokenType.ACCESS)),
        Depends(require_permission("visitors", PermissionAction.READ)),
    ],
)
async def get_visitors(db: DbSession):
    service_response = await visitor_service.get_visitor(db)
    return service_response


@router.post("/", response_model=RegisterVisitorResponse)
async def register_visitor(payload: RegisterVisitorRequest, db: DbSession):
    service_response = await visitor_jwt_service.register_and_generate_jwt(
        identifier_type=payload.identifier_type,
        identifier_value=payload.identifier_value,
        db=db,
    )
    return service_response


__all__ = ["router"]
