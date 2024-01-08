from pydantic import field_validator, BaseModel
from tracardi.service.plugin.domain.config import PluginConfig


class PluginConfiguration(PluginConfig):
    system: str = "c"
    city: str

    @field_validator("system")
    @classmethod
    def must_be_in(cls, value):
        if value.upper() not in ['F', 'C']:
            raise ValueError("Available values are 'F' or 'C'.")
        return value


class WeatherResult(BaseModel):
    temperature: float = None
    humidity: float = None
    wind_speed: float = None
    description: str = None
