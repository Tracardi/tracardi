from pydantic import BaseModel, validator


class Configuration(BaseModel):
    event_id: str

    @validator("event_id")
    def event_id_can_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Event id can not be empty")

        return value
