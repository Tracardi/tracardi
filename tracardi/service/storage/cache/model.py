from typing import Type

from pydantic import BaseModel

from tracardi.service.storage.redis.collections import Collection


def load(model: Type[BaseModel], id: str):
    pass


def save(storage: str, record: BaseModel):
    pass


def sync():
    pass
