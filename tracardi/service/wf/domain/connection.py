from pydantic import BaseModel


class Connection(BaseModel):
    node_id: str
    param: str
