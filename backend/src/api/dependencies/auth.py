from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.api.dependencies.db import get_db
from src.constant import TokenType
from src.errors import AuthRequestFailed
from src.models_db import RequestAuth, RequestSession
from src.repository_utils.requset_auth import get_request_session_by_id, get_request_register_by_id
from src.service.jwt_service import verify_jwt

oauth2_scheme = HTTPBearer()


def get_token_from_request(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if not token.credentials:
        AuthRequestFailed("No token provided")
    return token.credentials


async def get_token(
        token: str = Depends(get_token_from_request),
):
    payload = verify_jwt(token)
    if payload['sub'] is None:
        AuthRequestFailed("Wrong token provided")
    return payload


async def get_request_session(
        payload: dict = Depends(get_token),
        db: Session = Depends(get_db)
):
    if payload["type"] != TokenType.AUTH:
        raise AuthRequestFailed("Wrong token provided")
    request_id = payload["sub"]
    try:
        request = get_request_session_by_id(request_id, db)
    except SQLAlchemyError:
        raise AuthRequestFailed("Wrong token provided")
    return request


async def get_request_auth(
        payload: dict = Depends(get_token),
        db: Session = Depends(get_db)
):
    if payload["type"] != TokenType.REGISTER:
        raise AuthRequestFailed("Wrong token provided")
    request_id = payload["sub"]
    try:
        request = get_request_register_by_id(request_id, db)
    except SQLAlchemyError:
        raise AuthRequestFailed("Wrong token provided")
    return request
