from typing import Optional

from pydantic import BaseModel


class Tracker(BaseModel):
    url: str

    name: Optional[str] = None
