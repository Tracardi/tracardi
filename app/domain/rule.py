from typing import Optional
from pydantic import BaseModel


class Rule(BaseModel):
    scope: str
    name: str
    desc: Optional[str] = "No description"
    condition: str
    action: str

    def get_id(self):
        return self.name.lower().replace(" ", "-").replace("_", '-')



