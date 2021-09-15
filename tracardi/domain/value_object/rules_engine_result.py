from typing import Optional

from pydantic import BaseModel


class RulesEngineResult(BaseModel):
    triggered: int = 0
    errors: list = []
    details: Optional[dict] = None
