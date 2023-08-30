from pydantic import ConfigDict, BaseModel


class PluginConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
