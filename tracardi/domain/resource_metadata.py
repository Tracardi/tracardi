from typing import List, Optional

from pydantic import BaseModel


class ResourceMetadata(BaseModel):
    type: str
    name: str
    description: str
    traffic: str
    icon: str
    tags: List[str]
    plugin: List[str] = None

    def has_microservice_plugin(self) -> bool:
        return 'microservice' in self.tags and self.plugin is not None
