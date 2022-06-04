import uuid
from collections import defaultdict
from datetime import datetime
from typing import Optional, List, Union, Callable, Dict

from pydantic import BaseModel
from pydantic.utils import deep_update
from tracardi.service.notation.dot_accessor import DotAccessor
from .entity import Entity
from .metadata import ProfileMetadata
from .pii import PII
from .profile_traits import ProfileTraits
from .time import ProfileTime
from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo
from ..service.dot_notation_converter import DotNotationConverter
from .profile_stats import ProfileStats
from ..service.merger import merge
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
    segments: Optional[list] = []
    interests: Optional[dict] = {}
    consents: Optional[Dict[str, ConsentRevoke]] = {}
    active: bool = True

    def replace(self, profile):
        if isinstance(profile, Profile):
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
            # it has access only to profile. Other data is irrelevant
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

    async def merge(self, load_profiles_to_merge_callable: Callable, limit: int = 2000,
                    override_old_data: bool = True) -> Union['Profiles', None]:

        """
        This method mutates current profile.
        Merges profiles on keys set in profile.operation.merge. Loads profiles from database and
        combines its data into current profile. Returns Profiles object with profiles to be disables.
        It does not disable profiles or saves merged profile.
        """

        merge_key_values = self._get_merging_keys_and_values()

        # Are there any non-empty values in current profile

        if len(merge_key_values) > 0:

            # Load all profiles that match merging criteria
            existing_profiles = await load_profiles_to_merge_callable(
                merge_key_values,
                limit=limit)

            # Filter only profiles that are not current profile and where not merged
            profiles_to_merge = [p for p in existing_profiles if p.id != self.id and p.active is True]

            # Are there any profiles to merge?
            if len(profiles_to_merge) > 0:
                # Add current profile to existing ones and get merged profile
                merged_profile = Profiles.merge(profiles_to_merge, current_profile=self,
                                                override_old_data=override_old_data)

                # Replace current profile with merged profile
                self.replace(merged_profile)

                # Update profile after merge
                self.operation.update = True

                # Deactivate all other profiles except merged one

                profiles_to_disable = [p for p in existing_profiles if p.id != self.id]
                disabled_profiles = self._mark_profiles_as_merged(profiles_to_disable, merge_with=self.id)

                return Profiles(disabled_profiles)

        return None

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
            exclude={"operation": ...}
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


class Profiles(List[Profile]):

    @staticmethod
    def merge(existing_profiles: List[Profile], current_profile: Profile, override_old_data=True) -> Profile:

        all_profiles = existing_profiles + [current_profile]

        if override_old_data is False:
            """
                Marge do not loose data. Conflicts are resoled to list of values.
                E.g. Name="bill" + Name="Wiliam"  = Name=['bill','wiliam']
            """

            traits = [profile.traits.dict() for profile in all_profiles]
            piis = [profile.pii.dict() for profile in all_profiles]
            traits = merge({}, traits)
            piis = merge({}, piis)
        else:
            """
                Marge overrides data. Conflicts are resoled to single value. Latest wins.
                E.g. Name="bill" + Name="Wiliam" = Name='wiliam'
            """

            current_profile_dict = current_profile.dict()
            for profile in all_profiles:
                current_profile_dict['traits'] = deep_update(current_profile_dict['traits'], profile.traits.dict())
                current_profile_dict['pii'] = deep_update(current_profile_dict['pii'], profile.pii.dict())
            traits = current_profile_dict['traits']
            piis = current_profile_dict['pii']

        # Merge stats, consents, segments, etc.

        consents = {}
        segments = []
        interests = defaultdict(int)
        stats = ProfileStats()
        for profile in all_profiles:  # Type: Profile

            stats.visits += profile.stats.visits
            stats.views += profile.stats.views

            if isinstance(profile.segments, list):
                segments += profile.segments

            consents.update(profile.consents)

            for interest, count in profile.interests.items():
                interests[interest] += profile.interests[interest]

            # make uniq
            segments = list(set(segments))

        # Set id to merged id or current profile id.
        id = current_profile.metadata.merged_with if current_profile.metadata.merged_with is not None else current_profile.id

        return Profile(
            id=id,
            stats=stats,
            traits=traits,
            pii=piis,
            segments=segments,
            consents=consents,
            interests=dict(interests),
            active=True
        )
