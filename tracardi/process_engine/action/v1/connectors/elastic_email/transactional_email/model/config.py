from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.process_engine.action.v1.connectors.elastic_email.bulk_email.model.config import Message
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    sender_email: str
    message: Message

    @field_validator("sender_email")
    @classmethod
    def sender_email_subject(cls, value):
        if len(value) == 0:
            raise ValueError("Sender e-mail can not be empty.")
        return value
