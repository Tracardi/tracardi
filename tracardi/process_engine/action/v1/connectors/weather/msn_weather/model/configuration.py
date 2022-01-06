from pydantic import BaseModel, validator


class PluginConfiguration(BaseModel):
    system: str = "c"
    city: str

    @validator("system")
    def must_be_in(cls, value):
        if value.upper() not in ['F', 'C']:
            raise ValueError("Available values are 'F' or 'C'.")
        return value


class WeatherResult(BaseModel):
    temperature: float = None
    humidity: float = None
    wind_speed: float = None
    description: str = None
