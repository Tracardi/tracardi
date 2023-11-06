from typing import Any

from pydantic import BaseModel


class LoggerPayload(BaseModel):
    index: str
    entity: str
    payload: dict
