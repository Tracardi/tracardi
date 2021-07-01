import uuid
from datetime import datetime
from typing import Optional, Any
from .entity import Entity
from .metadata import Metadata
from .pii import PII
from .profile_traits import ProfileTraits
from .profile_stats import ProfileStats
from .time import Time
from app.service.storage.crud import StorageCrud
from .value_object.operation import Operation


class Profile(Entity):
    mergedWith: Optional[str] = None
    metadata: Optional[Metadata]
    operation: Operation = Operation()
    stats: ProfileStats = ProfileStats()
    traits: Optional[ProfileTraits] = ProfileTraits()
    pii: PII = PII()
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
        self.traits = profile.traits
        self.pii = profile.pii
        self.id = profile.id
        self.segments = profile.segments
        self.consents = profile.consents

    def merge(self, profile):
        self.stats.merge(profile.stats)
        self.traits.merge(profile.traits)
        self.pii.merge(profile.pii)
        self.segments = list(set(profile.segments + self.segments))
        # todo self.consents =

    def increase_visits(self, value=1):
        self.stats.visits += value

    def increase_views(self, value=1):
        self.stats.views += value

    def storage(self) -> StorageCrud:
        return StorageCrud("profile", Profile, entity=self, exclude={"operation": ...})

    @staticmethod
    def new() -> 'Profile':
        """
        @return Profile
        """
        return Profile(id=str(uuid.uuid4()))
