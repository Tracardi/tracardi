from typing import Optional
from pydantic import BaseModel


class PluginTestTemplate(BaseModel):
    init: Optional[dict]
    resource: Optional[dict] = None
