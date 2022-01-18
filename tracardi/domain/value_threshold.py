from datetime import datetime
from typing import Any, Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.record.value_threshold_record import ValueThresholdRecord
from tracardi.service.secrets import b64_encoder, b64_decoder


class ValueThreshold(NamedEntity):
    profile_id: Optional[str] = None
    timestamp: datetime
    ttl: int
    last_value: Any

    def encode(self) -> ValueThresholdRecord:
        return ValueThresholdRecord(
            id=self.id,
            name=self.name,
            profile_id=self.profile_id,
            timestamp=self.timestamp,
            ttl=self.ttl,
            last_value=b64_encoder(self.last_value),
        )

    @staticmethod
    def decode(record: ValueThresholdRecord) -> 'ValueThreshold':
        return ValueThreshold(
            id=record.id,
            name=record.name,
            profile_id=record.profile_id,
            timestamp=record.timestamp,
            ttl=record.ttl,
            last_value=b64_decoder(record.last_value),
        )
