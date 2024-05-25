from enum import Enum


class TokenType(str, Enum):
    REGISTER = "REGISTER"
    AUTH = "AUTH"


class CodeType(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
