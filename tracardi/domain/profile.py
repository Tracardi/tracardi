import uuid
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel
from tracardi.service.notation.dot_accessor import DotAccessor
from .entity import Entity
from .metadata import ProfileMetadata
from .named_entity import NamedEntity
from .pii import PII
from .profile_traits import ProfileTraits
from .storage_record import RecordMetadata
from .time import ProfileTime
from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo
from ..service.dot_notation_converter import DotNotationConverter
from .profile_stats import ProfileStats
from .segment import Segment
from ..process_engine.tql.condition import Condition


class ConsentRevoke(BaseModel):
    revoke: Optional[datetime] = None


class Profile(Entity):
    metadata: Optional[ProfileMetadata] = ProfileMetadata(time=ProfileTime())
    operation: Optional[Operation] = Operation()
    stats: ProfileStats = ProfileStats()
    traits: Optional[ProfileTraits] = ProfileTraits()
    pii: PII = PII()
    segments: Optional[List[str]] = []
    interests: Optional[dict] = {}
    consents: Optional[Dict[str, ConsentRevoke]] = {}
    active: bool = True
    aux: Optional[dict] = {}

    def serialize(self):
        return {
            "profile": self.dict(),
            "storage": self.get_meta_data().dict()
        }

    @staticmethod
    def deserialize(serialized_profile: dict) -> 'Profile':
        profile = Profile(**serialized_profile['profile'])
        profile.set_meta_data(RecordMetadata(**serialized_profile['storage']))
        return profile

    def replace(self, profile: 'Profile'):
        if isinstance(profile, Profile):
            # Make segments unique
            profile.segments = list(set(profile.segments))

            self.id = profile.id
            self.metadata = profile.metadata
            self.operation = profile.operation
            self.stats = profile.stats
            self.traits = profile.traits
            self.pii = profile.pii
            self.segments = profile.segments
            self.consents = profile.consents
            self.active = profile.active
            self.interests = profile.interests
            self.aux = profile.aux

    def get_merge_key_values(self) -> List[tuple]:
        converter = DotNotationConverter(self)
        return [converter.get_profile_file_value_pair(key) for key in self.operation.merge]

    def _get_merging_keys_and_values(self):
        merge_key_values = self.get_merge_key_values()

        # Add keyword
        merge_key_values = [(field, value) for field, value in merge_key_values if value is not None]

        return merge_key_values

    @staticmethod
    def _mark_profiles_as_merged(profiles, merge_with) -> List['Profile']:
        disabled_profiles = []

        for profile in profiles:  # type: Profile
            profile.active = False
            profile.metadata.merged_with = merge_with
            disabled_profiles.append(profile)

        return disabled_profiles

    async def segment(self, event_types, load_segments):

        """
        This method mutates current profile. Loads segments and adds segments to current profile.
        """

        # todo cache segments for 30 sec
        flat_profile = DotAccessor(
            profile=self
            # it has access only to profile. Other data is irrelevant because we check only profile.
        )

        for event_type in event_types:  # type: str

            # Segmentation is run for every event

            # todo segments are loaded one by one - maybe it is possible to load it at once
            # todo segments are loaded event if they are disabled. It is checked later. Maybe we can filter it here.
            segments = await load_segments(event_type, limit=500)

            for segment in segments:

                segment = Segment(**segment)

                if segment.enabled is False:
                    continue

                segment_id = segment.get_id()

                try:
                    condition = Condition()
                    if await condition.evaluate(segment.condition, flat_profile):
                        segments = set(self.segments)
                        segments.add(segment_id)
                        self.segments = list(segments)

                        # Yield only if segmentation triggered
                        yield event_type, segment_id, None

                except Exception as e:
                    msg = 'Condition id `{}` could not evaluate `{}`. The following error was raised: `{}`'.format(
                        segment_id, segment.condition, str(e).replace("\n", " "))

                    yield event_type, segment_id, msg

    def increase_visits(self, value=1):
        self.stats.visits += value
        self.operation.update = True

    def increase_views(self, value=1):
        self.stats.views += value
        self.operation.update = True

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'profile',
            Profile,
            exclude={"operation": ...},
            multi=True
        )

    @staticmethod
    def new() -> 'Profile':
        """
        @return Profile
        """
        return Profile(
            id=str(uuid.uuid4()),
            metadata=ProfileMetadata(time=ProfileTime(insert=datetime.utcnow()))
        )
