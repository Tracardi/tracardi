from pydantic import BaseModel


class Source(BaseModel):
    name: str
    hostname: str
    scope: str

    def get_id(self):
        return self.name.lower().replace(" ", "-").replace("_", '-')
