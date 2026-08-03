from app.constants.enum import TokenType, VisitorAppType
from app.services.iam.visitors import VisitorService
from app.services.utils.jwt import JwtUtils
from sqlalchemy.ext.asyncio import AsyncSession


class VisitorJwtService:
    def __init__(self, visitor_service: VisitorService, jwt_utils: JwtUtils):
        self.visitor_service = visitor_service
        self.jwt_utils = jwt_utils

    async def register_and_generate_jwt(
        self,
        identifier_type: str,
        identifier_value: str,
        app_type: VisitorAppType,
        db: AsyncSession,
    ):
        result = await self.visitor_service.register_visitor(
            identifier_type=identifier_type,
            identifier_value=identifier_value,
            app_type=app_type,
            db=db,
        )

        token, token_expired_at = self.jwt_utils.generate_token(
            token_type=TokenType.GUEST, visitor_id=result.id
        )
        return {
            "token": token,
            "token_expired_at": token_expired_at,
            "visitor": result,
        }
