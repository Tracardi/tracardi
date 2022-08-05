from pydantic import validator, AnyHttpUrl
from pydantic.main import BaseModel
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity


class AwsIamAuth(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str


class Content(BaseModel):
    content: str
    type: str

    @validator('content')
    def must_have_2_letters(cls, v):
        if len(v) < 2:
            raise ValueError('String is too short. String must be at least two letters long.')
        return v


class AwsSqsConfiguration(PluginConfig):
    source: NamedEntity
    message: Content
    region_name: str
    queue_url: AnyHttpUrl
    delay_seconds: int = 0
    message_attributes: str


class MessageAttribute:

    def __init__(self, value):
        self.value = value
        if isinstance(value, bool) or isinstance(value, str):
            self.type = "String"
            self.key = "StringValue"
            self.value = str(value)
        elif isinstance(value, int) or isinstance(value, float):
            self.type = "Number"
            self.key = "StringValue"
            self.value = str(value)
        else:
            self.type = "String"
            self.key = "StringValue"
            self.value = str(value)

    def dict(self):
        return {
            "DataType": self.type,
            self.key: self.value
        }


class MessageAttributes:

    def __init__(self, values: dict):
        self._value = {}
        for key, value in values.items():
            if isinstance(value, dict) or isinstance(value, list):
                raise ValueError("Attributes must be key value pairs. Allowed values are strings and "
                                 "numbers")
            self._value[key] = MessageAttribute(value)

    def dict(self):
        return {key: value.dict() for key, value in self._value.items()}
