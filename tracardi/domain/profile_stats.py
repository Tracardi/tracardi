from pydantic import BaseModel


class ProfileStats(BaseModel):
    visits: int = 0
    views: int = 0
    counters: dict = {}
