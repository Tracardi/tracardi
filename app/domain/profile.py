import uuid
from datetime import datetime
from typing import Optional, Any
from .entity import Entity
from .metadata import Metadata
from .profile_properties import ProfileProperties
from .profile_stats import ProfileStats
from .time import Time
from app.service.storage.crud import StorageCrud


class Profile(Entity):
    metadata: Optional[Metadata]
    stats: ProfileStats = ProfileStats()
    properties: Optional[ProfileProperties] = ProfileProperties()
    segments: Optional[list] = []
    consents: Optional[dict] = {}

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    def replace(self, profile):
        self.metadata = profile.metadata
        self.stats = profile.stats
        self.properties = profile.properties
        self.id = profile.id
        self.segments = profile.segments
        self.consents = profile.consents

    def increase_visits(self, value=1):
        self.stats.visits += value

    def increase_views(self, value=1):
        self.stats.views += value

    def storage(self) -> StorageCrud:
        return StorageCrud("profile", Profile, entity=self)

    @staticmethod
    def new() -> 'Profile':
        """
        @return Profile
        """
        return Profile(id=str(uuid.uuid4()))
