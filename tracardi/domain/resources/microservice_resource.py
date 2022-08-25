from pydantic import BaseModel

from tracardi.domain.named_entity import NamedEntity


class MicroserviceResource(BaseModel):
    url: str
    token: str
    service: NamedEntity
