import datetime
import uuid
from datetime import date

from pydantic import Field, model_validator, field_validator, BaseModel, Extra

from src.base_model import BaseDtoModel
from src.constant import CodeType


class RecordSessionResponse(BaseDtoModel):
    text: str
    token: str
    start_at: datetime
    duration: int

class UserResponse(BaseDtoModel):
    token: str
    text: str


class UserInput(BaseDtoModel):
    username: str


class AuthResponse(BaseDtoModel):
    code: str


class SessionUpdateResponse(BaseDtoModel):
    text: str
    update_at: datetime
    duration: int


class CodeInputModel(BaseDtoModel):
    code: str
    username: str

class CodeResponse(BaseDtoModel):
    type: CodeType