from pydantic import BaseModel, validator

from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    id: str
    type: NamedEntity
    reference_profile: bool = True

    @validator("id")
    def id_must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("This field can not be empty")
        return value.strip()

    @validator("type")
    def type_must_not_be_empty(cls, value):
        if value.id.strip() == "":
            raise ValueError("This field can not be empty")
        return value
