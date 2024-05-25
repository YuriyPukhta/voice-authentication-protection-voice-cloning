from src.base_model import BaseDtoModel


class UserCreate(BaseDtoModel):
    name: str

class RecordCreate(BaseDtoModel):
    path: str

class RequestSessionCreate(BaseDtoModel):
    text: str
