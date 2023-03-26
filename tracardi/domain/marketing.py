from typing import Optional

from pydantic import BaseModel


class UTM(BaseModel):
    source: Optional[str] = None
    medium: Optional[str] = None
    campaign: Optional[str] = None
    term: Optional[str] = None
    content: Optional[str] = None

    def is_empty(self) -> bool:
        return self.source is None
