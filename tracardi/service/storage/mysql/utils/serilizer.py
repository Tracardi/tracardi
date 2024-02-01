from typing import Optional, Type, List

import json

from pydantic import BaseModel


def to_json(data) -> str:
    if isinstance(data, BaseModel):
        return data.model_dump_json()
    if isinstance(data, list):
        return json.dumps([model.model_dump(mode='json') for model in data])
    return json.dumps(data, default=str)


def from_json(json_data: str, model: Optional[Type[BaseModel]] = None):

    if json_data is None:
        return None

    data = json.loads(json_data)

    if data is None:
        return None

    if model is None:
        return data

    return to_model(data, model)


def to_model(data, model: Type[BaseModel]):

    if not data:
        return None

    if isinstance(data, list):
        return [model(**item) for item in data]

    return model(**data)


def from_model(data) -> Optional[dict | List[dict]]:

    if not data:
        return data

    if isinstance(data, list):
        return [item.model_dump(mode='json') for item in data]

    return data.model_dump(mode='json')
