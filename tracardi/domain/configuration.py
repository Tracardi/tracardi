from pydantic import field_validator
from uuid import uuid4

from typing import Any, Optional, List

from datetime import datetime

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.utils.date import now_in_utc


class Configuration(NamedEntity):
    timestamp: Optional[datetime] = None
    config: dict
    description: Optional[str] = ""
    enabled: bool = False
    tags: Optional[List[str]] = []
    ttl: Optional[int] = 0

    def __init__(self, **data: Any):
        if 'id' not in data:
            data['id'] = str(uuid4())
        if data.get('timestamp', None) is None:
            data['timestamp'] = now_in_utc()

        super().__init__(**data)

    def get_token(self):
        return self.config.get("token", None)

    def get_repo_name(self):
        return self.config.get("repo_name", None)

    def get_repo_owner(self):
        return self.config.get("repo_owner", None)


