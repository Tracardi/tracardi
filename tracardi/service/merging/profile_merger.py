from system.adapter.os.bigdata.elastic.model.storage_record import RecordMetadata
from tracardi.common.dot_notation.dotdict import DotDict
from tracardi.service.merging.storage.loaders import load_duplicated_profiles_with_merge_key
from tracardi.service.merging.storage.mutation import save_flat_profile, delete_multiple_profiles, \
    move_profile_events_and_sessions

from tracardi.domain.profile_data import ProfileData

from tracardi.context import get_context
from tracardi.domain import ExtraInfo
from tracardi.domain.flat_profile import FlatProfile
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from pydantic.v1.utils import deep_update

from tracardi.domain.metadata import ProfileMetadata
from tracardi.domain.profile import Profile
from tracardi.domain.profile_stats import ProfileStats
from tracardi.domain.time import ProfileTime
from tracardi.common.logging.log_handler import get_logger

from tracardi.common.dot_notation.dot_notation_converter import DotNotationConverter

from tracardi.service.merging.merger import merge as dict_merge, get_conflicted_values, MergingStrategy

logger = get_logger(__name__)

async def _copy_duplicated_profiles_ids_to_merged_profile_ids(merged_profile: Profile,
                                                              duplicate_profiles: List[Profile]) -> Profile:
    merged_profile.ids.append(merged_profile.id)

    for dup_profile in duplicate_profiles:
        if isinstance(dup_profile.ids, list):
            merged_profile.ids += dup_profile.ids
    merged_profile.ids = list(set(merged_profile.ids))

    return merged_profile


class ProfileMerger:

    def __init__(self, profile: Profile):
        self.current_profile = profile

    @staticmethod
    def add_keywords(merge_by):
        _merge_by_keyword = []
        for name, value in merge_by:
            if name.startswith('traits.'):
                name = f"{name}.keyword"
            _merge_by_keyword.append((name, value))
        return _merge_by_keyword

    @staticmethod
    async def invoke_merge_profile(profile: Optional[Profile],
                                   merge_by: List[Tuple[str, str]],  # Field: value
                                   condition: str = 'must',
                                   limit: int = 2000) -> Optional[Profile]:

        if profile is None:
            logger.info("Method invoke_merge_profile can not merge on none existent profile. Profile equals None.")
            return None

        if len(merge_by) > 0:
            # Load all profiles that match merging criteria

            # CAUTION! Traits are indexed as text and keyword. So loading it by trains.name will not work
            # we need to load it by traits.name.keyword.

            # Here we are appending keyword for each trait.

            merge_by = ProfileMerger.add_keywords(merge_by)

            similar_profiles = await load_duplicated_profiles_with_merge_key(
                merge_by,
                condition=condition,
                limit=limit
            )

            logger.info(f"Loading profiles to merge in context {get_context()}. Found {len(similar_profiles)} "
                        f"similar profiles.")

            no_if_similar_profiles = len(similar_profiles)
            if no_if_similar_profiles == 0:
                logger.info("No similar profiles to merge")
                return None

            if no_if_similar_profiles == 1 and similar_profiles[0].id == profile.id:
                logger.info("No profiles to merge")
                return None

            return await ProfileMerger(profile).compute_one_profile(similar_profiles)

        return None

    @staticmethod
    def _get_merge_key_values(profile: Profile) -> List[tuple]:
        converter = DotNotationConverter(profile)
        values = [converter.get_profile_file_value_pair(key) for key in profile.get_merge_keys()]
        return values

    @staticmethod
    def get_merging_keys_and_values(profile: Profile) -> List[Tuple[str, str]]:
        merge_key_values = ProfileMerger._get_merge_key_values(profile)

        # Add keyword
        merge_key_values = [(field, value) for field, value in merge_key_values if value is not None]

        return merge_key_values

    @staticmethod
    def _deep_update(mapping: Dict, *updating_mappings: Dict) -> Dict:
        updated_mapping = mapping.copy()
        for updating_mapping in updating_mappings:
            for k, v in updating_mapping.items():
                if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                    updated_mapping[k] = deep_update(updated_mapping[k], v)
                elif v is not None:
                    updated_mapping[k] = v
        return updated_mapping

    def _merge_traits_and_data(self, _traits, _data, merging_strategy: MergingStrategy) -> Tuple[
        dict, ProfileData, dict]:

        profiles_data = [_profile_data.get('data', {}) for _profile_data in _data]

        # old_value = {
        #     'traits': _traits,
        #     "data": profiles_data
        # }

        new_value = {
            'traits': dict_merge({}, _traits, merging_strategy),
            'data': dict_merge({}, profiles_data, merging_strategy)
        }

        # conflicts_aux = get_conflicted_values(old_value, new_value)
        conflicts_aux = {}

        # This is the fix for merging error on location
        flat_new_values = DotDict(new_value)
        if 'data.devices.last.geo.location' in flat_new_values:
            del (flat_new_values['data.devices.last.geo.location'])
            if 'data.devices.last.geo.latitude' in flat_new_values and 'data.devices.last.geo.longitude' in flat_new_values:
                flat_new_values['data.devices.last.geo.location'] = [flat_new_values['data.devices.last.geo.latitude'],
                                                                     flat_new_values['data.devices.last.geo.longitude']]
            new_value = flat_new_values.to_dict()

        traits = new_value['traits']
        data = ProfileData(**new_value['data'])

        return traits, data, conflicts_aux

    @staticmethod
    def _get_primary_id(all_profiles) -> Optional[str]:
        primary_ids = {profile.primary_id for profile in all_profiles if profile.primary_id is not None}

        if len(primary_ids) == 0:
            return None

        if len(primary_ids) > 1:
            logger.warning(f"Primary ID conflict while merging. Expected Single primary id got {primary_ids}.")

        return list(primary_ids)[0]

    def _get_merged_profile(self,
                            similar_profiles: List[Profile],
                            merging_strategy: MergingStrategy,
                            merge_stats: bool = True,
                            merge_time: bool = True
                            ) -> Profile:

        all_profiles = [self.current_profile] + similar_profiles

        # Get primary ID

        primary_id = self._get_primary_id(all_profiles)

        # Merge traits and piis

        _traits = [profile.traits for profile in all_profiles]
        _data = [profile.model_dump(mode="json") for profile in all_profiles]
        traits, data, conflicts_aux = self._merge_traits_and_data(_traits, _data, merging_strategy)

        # Merge stats, consents, segments, etc.

        consents = {}
        segments = []
        interests = {}
        stats = ProfileStats()
        time = ProfileTime(**self.current_profile.metadata.time.model_dump(mode='json'))
        time.visit.count = 0  # Reset counter - it sums all the visits

        for profile in all_profiles:  # Type: Profile

            # Time
            if merge_time:
                time.visit.count += profile.metadata.time.visit.count

                if isinstance(time.insert, datetime) and isinstance(profile.metadata.time.insert, datetime):
                    # Get earlier date
                    if time.insert > profile.metadata.time.insert:
                        time.insert = profile.metadata.time.insert

                if isinstance(time.visit.current, datetime) and isinstance(profile.metadata.time.visit.current,
                                                                           datetime):
                    if time.visit.current < profile.metadata.time.visit.current:
                        time.visit.current = profile.metadata.time.visit.current

                if isinstance(time.visit.last, datetime) and isinstance(profile.metadata.time.visit.last, datetime):
                    if time.visit.last < profile.metadata.time.visit.last:
                        time.visit.last = profile.metadata.time.visit.last

            # Stats

            if merge_stats:
                stats.visits += profile.stats.visits
                stats.views += profile.stats.views

                for key, value in profile.stats.counters.items():
                    if key not in stats.counters:
                        stats.counters[key] = 0
                    stats.counters[key] += value

            # Segments

            if isinstance(profile.segments, list):
                segments += profile.segments
                segments = list(set(segments))

            # Consents

            consents.update(profile.consents)

            # Interests
            # TODO use dict_merge it does is automatically

            for interest, count in profile.interests.items():
                if interest not in interests:
                    interests[interest] = 0
                interests[interest] += profile.interests[interest]

        # self.current_profile.aux["conflicts"] = conflicts_aux

        profile = Profile(
            metadata=ProfileMetadata(time=time),
            id=self.current_profile.id,
            primary_id=primary_id,
            ids=self.current_profile.ids,
            stats=stats if merge_stats else self.current_profile.stats,
            traits=traits,
            data=data,
            segments=segments,
            consents=consents,
            interests=dict(interests),
            active=True,
            aux=self.current_profile.aux
        )

        profile.set_meta_data(self.current_profile.get_meta_data())
        profile.mark_for_update()
        # Removed not needed to always hash IDS. Hash only on update.
        # profile.hash_all_allowed_pii_as_ids()

        return profile

    async def merge(self, similar_profiles: List[Profile]) -> Tuple[Optional[Profile], List[Profile]]:

        return await self._merge(
            similar_profiles,
            allow_duplicate_ids=False
        )

    async def deduplicate(self,
                          similar_profiles: List[Profile]) -> Tuple[Optional[Profile], List[Profile]]:
        return await self._merge(
            similar_profiles,
            allow_duplicate_ids=True
        )

    async def _merge(self,
                     similar_profiles: List[Profile],
                     allow_duplicate_ids: bool = False
                     ) -> Tuple[Optional[Profile], List[Profile]]:
        """
        Merges profiles on keys set in profile.get_merge_keys(). Loads profiles from database and
        combines its data into current profile. Returns Profiles object with profiles to be disabled.
        It does not disable profiles or saves merged profile.
        """

        merged_profile = None

        if len(similar_profiles) == 0:
            return merged_profile, []

        if not allow_duplicate_ids:
            # Filter only profiles that are not current profile and where not merged
            profiles_to_merge = [p for p in similar_profiles if p.id != self.current_profile.id]
        else:
            profiles_to_merge = similar_profiles

        # Are there any profiles to merge?
        if len(profiles_to_merge) > 0:
            # Add current profile to existing ones and get merged profile

            merging_strategy = MergingStrategy()
            merged_profile = self._get_merged_profile(
                profiles_to_merge,
                merging_strategy
            )

        return merged_profile, profiles_to_merge

    async def compute_one_profile(self, similar_profiles: List[Profile]):

        # Merge
        merged_profile, duplicate_profiles = await self.merge(similar_profiles)

        # Update events and sessions to mark the new merged profile

        if merged_profile:

            logger.info(f"Updating events and session during merge. Setting primary ID to {merged_profile.id}.",
                        extra=ExtraInfo.build(origin="merging", object=self))

            # Copy ids
            merged_profile = await _copy_duplicated_profiles_ids_to_merged_profile_ids(
                merged_profile,
                duplicate_profiles)

            merged_profile.metadata.system.remove_merging_data()

            # Auto refresh db
            merged_flat_profile = FlatProfile.from_profile(merged_profile)
            await save_flat_profile(merged_flat_profile, refresh=True)

            # Schedule - move events from duplicated profiles
            duplicated_profile_ids = list({_profile.id for _profile in duplicate_profiles})
            await move_profile_events_and_sessions(duplicated_profile_ids, merged_profile.id)

            # Schedule - mark duplicated profiles
            records_to_delete: List[Tuple[str, RecordMetadata]] = [(profile.id, profile.get_meta_data())
                                                                   for profile in duplicate_profiles]

            logger.debug(f"Profiles to delete {records_to_delete}.",
                         extra=ExtraInfo.build(origin="merging", object=self))

            await delete_multiple_profiles(records_to_delete)

            # Replace current profile with merged profile
            return merged_profile

        else:
            logger.info("No need to merge")

        return None
