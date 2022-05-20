from datetime import datetime

from pydantic import BaseModel


class Mapping(BaseModel):
    date: datetime
    version: str
    index_name: str
    index: str
    mapping: dict
