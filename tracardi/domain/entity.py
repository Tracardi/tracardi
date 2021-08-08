from uuid import uuid4
from pydantic import BaseModel
import tracardi.service.storage.crud as crud


class Entity(BaseModel):
    id: str

    def storage(self, index) -> 'crud.EntityStorageCrud':
        return crud.EntityStorageCrud(index, entity=self)

    @staticmethod
    def new() -> 'Entity':
        return Entity(id=str(uuid4()))
