from typing import Optional, Type

import json

from pydantic import BaseModel


def to_json(data) -> str:
    if isinstance(data, BaseModel):
        return data.model_dump_json()
    return json.dumps(data, default=str)


def from_json(json_data: str, model: Optional[Type] = None):

    if json_data is None:
        return None

    data = json.loads(json_data)

    if data is None:
        return None

    if model is None:
        return data
    return model(**data)
