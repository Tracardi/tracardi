from pydantic import BaseModel


class PluginConfig(BaseModel):
    class Config:
        frozen = True
