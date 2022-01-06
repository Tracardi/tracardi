from typing import Any
from pydantic import BaseModel


class InputParams(BaseModel):
    port: str
    value: Any
