import uuid
import jwt
from datetime import datetime, timedelta

from jwt import PyJWTError

from src.config import AppConfig
from src.constant import TokenType
from src.errors import AuthRequestFailed


config = AppConfig()


def create_jwt_auth(guid: str) -> str:
    return create_jwt(guid, config.AUTH_TOKEN_EXPIRATION, TokenType.AUTH)


def create_jwt_register(guid: str, ) -> str:
    return create_jwt(guid, config.REGISTER_TOKEN_EXPIRATION, TokenType.REGISTER)


def create_jwt(guid: str, exp_in_minute: int, type: TokenType) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=exp_in_minute)
    payload = {
        "sub": str(guid),
        "exp": expiration,
        "type": type
    }

    token = jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return token


def verify_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except PyJWTError:
        raise AuthRequestFailed("Token expired")
