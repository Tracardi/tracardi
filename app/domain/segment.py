from typing import Optional
from pydantic import BaseModel


class Segment(BaseModel):
    scope: str
    name: str
    desc: Optional[str] = "No description"
    condition: str

    def get_id(self):
        return self.name.lower().replace(" ", "-").replace("_", '-')
