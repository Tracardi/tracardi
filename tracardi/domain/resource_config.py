from pydantic import BaseModel

from tracardi.domain.resource_id import ResourceId


class ResourceConfig(BaseModel):
    source: ResourceId
