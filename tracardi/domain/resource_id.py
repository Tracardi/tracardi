from pydantic import BaseModel, validator


class ResourceId(BaseModel):
    id: str

    @validator("id")
    def id_not_empty(cls, value):
        if not value:
            raise ValueError("Resource must not be empty.")
        return value
