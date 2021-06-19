from typing import Optional

from pydantic import BaseModel


class Context(BaseModel):
    config: Optional[dict] = {}
    params: Optional[dict] = {}
