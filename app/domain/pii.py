from typing import Optional

from pydantic import BaseModel


class PII(BaseModel):
    name: Optional[str] = ''
    surname: Optional[str] = ''
    birthData: Optional[int] = None
    email: Optional[str] = ''
    telephone: Optional[str] = ''
    other: Optional[dict] = {}
