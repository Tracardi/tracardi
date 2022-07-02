from pydantic import BaseModel


class PluginConfig(BaseModel):
    class Config:
        allow_mutation = False
