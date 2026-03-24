import datetime
import uuid

import jwt

from app.auth.auth_info import AuthInfo
from app.core.config import Settings


class JWTService:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret
        self._algorithm = settings.jwt_algorithm
        self._access_expire_hours = settings.jwt_access_token_expire_hours
        self._refresh_expire_days = settings.jwt_refresh_token_expire_days

    def create_access_token(self, user_id: uuid.UUID, email: str) -> str:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            hours=self._access_expire_hours
        )
        return jwt.encode(
            {"sub": str(user_id), "email": email, "exp": expire, "type": "access"},
            self._secret,
            algorithm=self._algorithm,
        )

    def create_refresh_token(self, user_id: uuid.UUID) -> str:
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            days=self._refresh_expire_days
        )
        return jwt.encode(
            {"sub": str(user_id), "exp": expire, "type": "refresh"},
            self._secret,
            algorithm=self._algorithm,
        )

    def verify_access_token(self, token: str) -> AuthInfo:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

        if payload.get("type") != "access":
            raise ValueError("Invalid token type")

        return AuthInfo(
            user_id=uuid.UUID(payload["sub"]),
            email=payload["email"],
        )

    def verify_refresh_token(self, token: str) -> uuid.UUID:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        return uuid.UUID(payload["sub"])
