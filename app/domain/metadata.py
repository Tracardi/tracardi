from pydantic import BaseModel
from app.domain.time import Time


class Metadata(BaseModel):
    time: Time
