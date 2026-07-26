from app.constants.enum import TokenType
from app.middleware.authenticate_helper import (
    authenticate_access_dependency,
    authenticate_guest_dependency,
    authenticate_refresh_dependency,
)
from app.middleware.authorize_helper import require_permission, require_permissions
from app.services.iam.identity import IdentityService
from app.services.iam.session import SessionService
from app.services.iam.visitors import VisitorService
from app.services.utils.jwt import JwtUtils

jwt_utils = JwtUtils()
visitor_service = VisitorService()
session_service = SessionService()
identity_service = IdentityService()


def authenticate(token_type: TokenType):
    if token_type == TokenType.GUEST:
        return authenticate_guest_dependency
    if token_type == TokenType.ACCESS:
        return authenticate_access_dependency
    if token_type == TokenType.REFRESH:
        return authenticate_refresh_dependency
    raise ValueError(f"Invalid token type: {token_type}")


__all__ = ["authenticate", "require_permission", "require_permissions"]
