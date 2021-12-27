from pydantic import BaseModel, validator


class Configuration(BaseModel):
    query: str

    @validator("query")
    def query_can_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Profile query can not be empty")

        return value
