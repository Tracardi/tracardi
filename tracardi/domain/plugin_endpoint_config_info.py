from pydantic import BaseModel


class PluginEndpointConfigInfo(BaseModel):
    config: dict
    production: bool
