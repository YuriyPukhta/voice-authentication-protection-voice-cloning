from pydantic.v1 import BaseSettings


class AppConfig (BaseSettings):
    REGISTER_TOKEN_EXPIRATION = 10
    AUTH_TOKEN_EXPIRATION = 15
    SECRET_KEY = "your_secret_key"
    ALGORITHM = "HS256"
    SIMILARITY_LIMIT = 0.9
    TIME_FOR_RECORD = 60
