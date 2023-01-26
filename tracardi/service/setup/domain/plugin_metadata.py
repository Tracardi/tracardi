from typing import Optional
from pydantic import BaseModel


class PluginTest(BaseModel):
    init: Optional[dict]
    resource: Optional[dict] = None


class PluginMetadata(BaseModel):
    test: PluginTest
