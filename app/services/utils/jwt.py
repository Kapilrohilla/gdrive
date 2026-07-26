import datetime
import uuid

import jwt
from app.config import settings
from app.constants.enum import TokenType

JWT_ALGO = "HS256"
GUEST_EXPIRY_DAYS = 300
ACCESS_EXPIRY_HOUR = 1
REFRESH_EXPIRY_DAYS = 30


class JwtUtils:
    def generate_token(
        self,
        token_type: TokenType,
        visitor_id: uuid.UUID,
        session_id: uuid.UUID | None = None,
        identity_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
    ):
        if token_type == TokenType.GUEST:
            return self._generate_guest_token(visitor_id=visitor_id)
        if token_type == TokenType.ACCESS:
            if user_id is None or identity_id is None or session_id is None:
                raise ValueError(
                    "User ID, identity ID, and session ID are required for access token"
                )
            return self._generate_access_token(
                user_id=user_id,
                identity_id=identity_id,
                visitor_id=visitor_id,
                session_id=session_id,
            )
        if token_type == TokenType.REFRESH:
            if user_id is None or identity_id is None or session_id is None:
                raise ValueError(
                    "User ID, identity ID, and session ID are required for refresh token"
                )
            return self._generate_refresh_token(
                user_id=user_id,
                identity_id=identity_id,
                visitor_id=visitor_id,
                session_id=session_id,
            )
        raise ValueError(f"Invalid token type: {token_type}")

    def _generate_guest_token(self, visitor_id: uuid.UUID):
        expired_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=GUEST_EXPIRY_DAYS
        )

        jwt_payload = {
            "token_type": TokenType.GUEST,
            "visitor_id": str(visitor_id),
            "exp": expired_at,
        }
        encoded_jwt = jwt.encode(payload=jwt_payload, key=settings.jwt_secret, algorithm=JWT_ALGO)
        return encoded_jwt, expired_at

    def _generate_access_token(
        self,
        user_id: uuid.UUID,
        identity_id: uuid.UUID,
        visitor_id: uuid.UUID,
        session_id: uuid.UUID,
    ):
        expired_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            hours=ACCESS_EXPIRY_HOUR
        )
        jwt_payload = {
            "token_type": TokenType.ACCESS,
            "user_id": str(user_id),
            "identity_id": str(identity_id),
            "visitor_id": str(visitor_id),
            "session_id": str(session_id),
            "exp": expired_at,
        }
        encoded_jwt = jwt.encode(payload=jwt_payload, key=settings.jwt_secret, algorithm=JWT_ALGO)
        return encoded_jwt, expired_at

    def _generate_refresh_token(
        self,
        user_id: uuid.UUID,
        identity_id: uuid.UUID,
        visitor_id: uuid.UUID,
        session_id: uuid.UUID,
    ):
        expired_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=REFRESH_EXPIRY_DAYS
        )
        jwt_payload = {
            "token_type": TokenType.REFRESH,
            "user_id": str(user_id),
            "identity_id": str(identity_id),
            "visitor_id": str(visitor_id),
            "session_id": str(session_id),
            "exp": expired_at,
        }
        encoded_jwt = jwt.encode(payload=jwt_payload, key=settings.jwt_secret, algorithm=JWT_ALGO)
        return encoded_jwt, expired_at

    def verify_token(self, token_type: TokenType, token: str) -> dict:
        data = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGO])

        if (
            (token_type == TokenType.GUEST and data.get("token_type") != TokenType.GUEST)
            or (token_type == TokenType.ACCESS and data.get("token_type") != TokenType.ACCESS)
            or (token_type == TokenType.REFRESH and data.get("token_type") != TokenType.REFRESH)
        ):
            raise ValueError("Invalid token type")

        return data
