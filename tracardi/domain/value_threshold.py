from datetime import datetime
from typing import Any, Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.secrets import b64_encoder, b64_decoder


class ValueThreshold(NamedEntity):
    profile_id: Optional[str] = None
    timestamp: datetime
    ttl: int
    last_value: Any

    def encode(self) -> str:
        return b64_encoder(self.model_dump())

    @staticmethod
    def decode(record: str) -> 'ValueThreshold':
        return ValueThreshold(**b64_decoder(record))
