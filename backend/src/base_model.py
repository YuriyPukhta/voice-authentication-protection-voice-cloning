from pydantic import BaseModel, Extra


class BaseDtoModel(BaseModel):
    class Config:
        extra = Extra.ignore
        populate_by_name = True
        arbitrary_types_allowed = True
        from_attributes = True

