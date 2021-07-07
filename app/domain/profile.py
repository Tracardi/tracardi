import uuid
from datetime import datetime
from typing import Optional, Any, List
from .entity import Entity
from .metadata import Metadata
from .pii import PII
from .profile_traits import ProfileTraits
from .time import Time
from ..service.dot_notation_converter import DotNotationConverter
from ..service.storage.collection_crud import CollectionCrud
from ..service.storage.crud import StorageCrud
import app.domain.value_object.operation
from typing import List
from uuid import uuid4
from .profile_stats import ProfileStats
from ..service.merger import merge


class Profile(Entity):
    mergedWith: Optional[str] = None
    metadata: Optional[Metadata]
    operation: Optional[app.domain.value_object.operation.Operation] = app.domain.value_object.operation.Operation()
    stats: ProfileStats = ProfileStats()
    traits: Optional[ProfileTraits] = ProfileTraits()
    pii: PII = PII()
    segments: Optional[list] = []
    consents: Optional[dict] = {}
    active: bool = True

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
        self.active = profile.active
        self.mergedWith = profile.mergedWith

    def get_merge_key_values(self) -> List[tuple]:
        converter = DotNotationConverter(self)
        return [converter.get_profile_fiel_value_pair(key) for key in self.operation.merge]

    def merge(self, profile):
        """
        Merges profiles. Merged properties are: stats, traits, pii, segments, consents.
        """

        self.stats = self.stats.merge(profile.stats)
        self.traits = self.traits.merge(profile.traits)
        self.pii = self.pii.merge(profile.pii)
        self.segments = list(set(profile.segments + self.segments))
        self.consents.update(profile.consents)

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


class Profiles(list):

    @staticmethod
    def merge(existing_profiles: List[Profile], current_profile: Profile) -> Profile:

        profiles = existing_profiles + [current_profile]

        traits = [profile.traits.dict() for profile in profiles]
        traits = merge({}, traits)

        piis = [profile.pii.dict() for profile in profiles]
        piis = merge({}, piis)

        consents = {}
        segments = []
        stats = ProfileStats()
        for profile in profiles:
            stats.visits += profile.stats.visits
            stats.views += profile.stats.views

            if isinstance(profile.segments, list):
                segments += profile.segments

            consents.update(profile.consents)

            # make uniq
            segments = list(set(segments))

        # Set id to merged id or current profile id.
        id = current_profile.mergedWith if current_profile.mergedWith is not None else current_profile.id

        return Profile(
            id=id,
            mergedWith=None,
            stats=stats,
            traits=traits,
            pii=piis,
            segments=segments,
            consents=consents,
            active=True
        )

    def bulk(self) -> CollectionCrud:
        return CollectionCrud("profile", self)
