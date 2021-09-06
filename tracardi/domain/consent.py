from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.domain.third_party_processor import ThirdPartyProcessor
from tracardi.domain.time_range_query import DatetimePayload


class Consent(Entity):
    description: Optional[str] = None
    third_party_processor: Optional[ThirdPartyProcessor] = None
    revoke: Optional[DatetimePayload] = None
