from pydantic import field_validator, BaseModel


class ResourceId(BaseModel):
    id: str

    @field_validator("id")
    @classmethod
    def id_not_empty(cls, value):
        if not value:
            raise ValueError("Resource must not be empty.")
        return value
