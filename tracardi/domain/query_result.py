from pydantic import BaseModel


class QueryResult(BaseModel):
    total: int
    result: list