from pydantic import BaseModel


class ErrorDebugInfo(BaseModel):
    msg: str
    line: int
    file: str
