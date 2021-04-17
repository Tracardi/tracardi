from typing import Optional
from pydantic import BaseModel


class Segment(BaseModel):
    scope: str
    name: str
    description: Optional[str] = "No description"
    tags: Optional[list] = []
    condition: str

    def get_id(self):
        return self.name.lower().replace(" ", "-").replace("_", '-')
