import copy
import uuid
from datetime import datetime
from typing import Optional, Any, List, Tuple, Union

from .entity import Entity
from .metadata import Metadata
from .pii import PII
from .profile_traits import ProfileTraits
from .time import Time
from ..service.dot_notation_converter import DotNotationConverter
from ..service.storage.collection_crud import CollectionCrud
from ..service.storage.crud import StorageCrud
import tracardi.domain.value_object.operation

from .profile_stats import ProfileStats
from ..service.merger import merge
from .segment import Segment
from .segments import Segments
from ..process_engine.tql.condition import Condition
from ..process_engine.tql.utils.dictonary import flatten


class Profile(Entity):
    mergedWith: Optional[str] = None
    metadata: Optional[Metadata]
    operation: Optional[tracardi.domain.value_object.operation.Operation] = tracardi.domain.value_object.operation.Operation()
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
        self.operation = profile.operation

    def get_merge_key_values(self) -> List[tuple]:
        converter = DotNotationConverter(self)
        return [converter.get_profile_fiel_value_pair(key) for key in self.operation.merge]

    def _get_merging_keys_and_values(self):
        merge_key_values = self.get_merge_key_values()

        # Add keyword
        merge_key_values = [(f"{field}.keyword", value) for field, value in merge_key_values if value is not None]

        return merge_key_values

    @staticmethod
    def _mark_profiles_as_merged(profiles, merge_with) -> List['Profile']:
        disabled_profiles = []

        for profile in profiles:
            profile.active = False
            profile.mergedWith = merge_with
            disabled_profiles.append(profile)

        return disabled_profiles

    async def segment(self, event_types):

        """
        This method mutates current profile. Loads segments and adds segments to current profile.
        """

        # todo cache segments for 30 sec
        flat_payload = flatten(copy.deepcopy(self.dict()))

        for event_type in event_types:  # type: str

            # Segmentation is run for every event

            # todo segments are loaded one by one - maybe it is possible to load it at once
            segments = await Segments.storage().load_by('eventType.keyword', event_type)
            for segment in segments:

                segment = Segment(**segment)
                segment_id = segment.get_id()

                try:

                    if Condition.evaluate(segment.condition, flat_payload):
                        segments = set(self.segments)
                        segments.add(segment_id)
                        self.segments = list(segments)

                        # Yield only if segmentation triggered
                        yield event_type, segment_id, None

                except Exception as e:
                    msg = 'Condition id `{}` could not evaluate `{}`. The following error was raised: `{}`'.format(
                        segment_id, segment.condition, str(e).replace("\n", " "))

                    yield event_type, segment_id, msg

    async def merge(self, limit=2000) -> Union['Profiles', None]:

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
            existing_profiles = await tracardi.domain.value_object.operation.Operation.load_profiles_to_merge(
                merge_key_values,
                limit=limit)

            # Filter only profiles that are not current profile and where not merged
            profiles_to_merge = [p for p in existing_profiles if p.id != self.id and p.active is True]

            print('profiles_to_merge',profiles_to_merge)

            # Are there any profiles to merge?
            if len(profiles_to_merge) > 0:
                # Add current profile to existing ones and get merged profile
                merged_profile = Profiles.merge(profiles_to_merge, self)

                # Replace current profile with merged profile
                self.replace(merged_profile)

                # Deactivate all other profiles except merged one

                profiles_to_disable = [p for p in existing_profiles if p.id != self.id]
                disabled_profiles = self._mark_profiles_as_merged(profiles_to_disable, merge_with=self.id)

                return Profiles(disabled_profiles)

        return None

    def increase_visits(self, value=1):
        self.stats.visits += value

    def increase_views(self, value=1):
        self.stats.views += value

    def storage(self) -> StorageCrud:
        return StorageCrud("profile", Profile, entity=self, exclude={"operation": ...})

    @staticmethod
    async def load_current(id) -> 'Profile':

        """
        Loads current profile. If profile was merged then it loads merged profile.
        """

        entity = Entity(id=id)
        profile = await entity.storage('profile').load(Profile)  # type: Profile
        if profile is not None and profile.mergedWith is not None:
            profile = await Profile.load_current(profile.mergedWith)
        return profile

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
