from typing import Optional

from pydantic import field_validator, BaseModel

from tracardi.domain.named_entity import NamedEntity


class ElasticCredentials(BaseModel):
    url: str
    port: int  # todo remove port not used
    scheme: str
    username: Optional[str] = None
    password: Optional[str] = None
    verify_certs: bool

    def has_credentials(self):
        return self.username is not None and self.password is not None


class ElasticResourceConfig(BaseModel):
    source: NamedEntity

    @field_validator("source")
    @classmethod
    def validate_named_entities(cls, value):
        if not value.id:
            raise ValueError("This field cannot be empty.")
        return value
