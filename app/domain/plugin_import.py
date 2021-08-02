from typing import Optional

from pydantic import BaseModel


class PluginImport(BaseModel):
    module: str
    upgrade: Optional[bool] = False
