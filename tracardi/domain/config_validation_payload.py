from typing import Optional

from pydantic import BaseModel


class ConfigValidationPayload(BaseModel):
    config: dict = None
    credentials: Optional[dict] = None
