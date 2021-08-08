from pydantic import BaseModel
from tracardi.domain.time import Time


class Metadata(BaseModel):
    time: Time
