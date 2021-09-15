from pydantic import BaseModel
from tracardi.domain.value_object.save_result import SaveResult


class CollectResult(BaseModel):
    session: SaveResult
    events: SaveResult
    profile: SaveResult
