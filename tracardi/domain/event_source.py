from urllib.parse import urlparse, ParseResult

from datetime import datetime
from typing import Optional, Union, List, Any

from tracardi.domain.named_entity import NamedEntity, NamedEntityInContext
from tracardi.service.utils.date import now_in_utc


class EventSource(NamedEntityInContext):
    type: List[str]
    bridge: NamedEntity
    timestamp: Optional[datetime]
    description: Optional[str] = "No description provided"
    channel: Optional[str] = ""
    enabled: Optional[bool] = True
    transitional: Optional[bool] = False
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    permanent_profile_id: Optional[bool] = False
    requires_consent: Optional[bool] = False
    manual: Optional[str] = None
    locked: bool = False
    synchronize_profiles: bool = True
    config: Optional[dict] = None

    def __init__(self, **data: Any):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = now_in_utc()
        if 'type' in data and isinstance(data['type'], str):
            data['type'] = [data['type']]

        super().__init__(**data)

    def is_allowed(self, allowed_types) -> bool:
        return bool(set(self.type).intersection(set(allowed_types)))

    def has_restricted_domain(self) -> bool:

        if not isinstance(self.config, dict):
            return False

        if 'restrict_to' not in self.config or 'restriction' not in self.config:
            return False

        domain: Optional[str] = self.get_restricted_domain()
        restrict_to: Optional[str] = self.get_restriction_type()

        if not domain or not restrict_to:
            return False

        return True

    def get_restricted_domain(self) -> Optional[ParseResult]:
        try:

            if not isinstance(self.config, dict):
                return None

            domain: Optional[str] = self.config.get('restriction', "")
            domain = domain.strip()

            if not domain:
                return None

            url = urlparse(domain)
            if not url.scheme or not url.netloc:
                # Return original value
                return urlparse(f"http://{domain}")
            return url

        except KeyError:
            return None

    def get_restriction_type(self) -> Optional[str]:
        try:

            if not isinstance(self.config, dict):
                return None

            restrict_to: Optional[str] = self.config.get('restrict_to', "")
            restrict_to = restrict_to.strip()

            if not restrict_to:
                return None

            if restrict_to.lower() == "none":
                return None
            return restrict_to
        except KeyError:
            return None

    def is_allowed_domain_origin(self, origin: ParseResult) -> bool:
        restrict_to = self.get_restricted_domain()
        if not restrict_to:
            return True

        type_of_restriction = self.get_restriction_type()
        if not type_of_restriction:
            return True

        return restrict_to.hostname.lower().strip() == origin.hostname.lower().strip()
