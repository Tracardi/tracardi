from typing import Optional

from pydantic import BaseModel
from app.domain.time import Time


class Metadata(BaseModel):
    time: Time
    new: Optional[bool] = False
    updated: Optional[bool] = False
