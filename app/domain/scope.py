from pydantic import BaseModel


class Scope(BaseModel):
    name: str
    host: str

    def get_id(self):
        return self.name.lower().replace(" ", "-").replace("_", '-')
