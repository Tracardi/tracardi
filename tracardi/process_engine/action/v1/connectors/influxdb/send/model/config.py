from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    source: NamedEntity
    database: str

    @validator("database")
    def validate_database(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class InfluxCredentials(BaseModel):
    host: str
    port: int
    username: str
    password: str
