from typing import Optional
from pydantic import BaseModel


class Rule(BaseModel):
    scope: str
    name: str
    description: Optional[str] = "No description"
    condition: str
    actions: list
    tags: Optional[list] = []

    def get_id(self):
        return self.name.lower().replace(" ", "-").replace("_", '-')



