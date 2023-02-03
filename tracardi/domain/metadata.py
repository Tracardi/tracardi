from typing import Optional

from pydantic import BaseModel
from tracardi.domain.time import Time, ProfileTime


class Metadata(BaseModel):
    time: Time


class ProfileMetadata(BaseModel):
    time: ProfileTime
    aux: Optional[dict] = {}
