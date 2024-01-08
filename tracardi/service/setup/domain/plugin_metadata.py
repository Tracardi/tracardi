from typing import Optional
from pydantic import BaseModel


class PluginTest(BaseModel):
    init: Optional[dict] = None
    resource: Optional[dict] = None


class PluginMetadata(BaseModel):
    test: PluginTest
    plugin_registry: Optional[str] = None
