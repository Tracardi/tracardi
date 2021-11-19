from typing import List

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    roles: List[str]

    def authorization_header(self):
        return {"Authorization": f"Bearer {self.access_token}"}
