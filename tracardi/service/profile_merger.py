import asyncio
import logging
from tracardi.service.tracking.storage.profile_storage import save_profile, delete_profile

from tracardi.domain.profile_data import ProfileData

from .tracking.cache.profile_cache import delete_profile_cache, save_profile_cache
from ..context import get_context
from ..domain.storage_record import RecordMetadata
from tracardi.service.storage.driver.elastic import event as event_db
from tracardi.service.storage.driver.elastic import session as session_db
from tracardi.service.storage.driver.elastic import profile as profile_db
from tracardi.service.storage.driver.elastic import raw as raw_db
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from pydantic.v1.utils import deep_update

from ..config import tracardi
from ..domain.metadata import ProfileMetadata
from ..domain.profile import Profile
from ..domain.profile_stats import ProfileStats
from ..domain.time import ProfileTime
from ..exceptions.log_handler import log_handler
from ..service.dot_notation_converter import DotNotationConverter

from tracardi.service.merging.merger import merge as dict_merge, get_conflicted_values, MergingStrategy

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def _copy_duplicated_profiles_ids_to_merged_profile_ids(merged_profile: Profile,
                                                              duplicate_profiles: List[Profile]) -> Profile:
    merged_profile.ids.append(merged_profile.id)

    for dup_profile in duplicate_profiles:
        if isinstance(dup_profile.ids, list):
            merged_profile.ids += dup_profile.ids
    merged_profile.ids = list(set(merged_profile.ids))

    return merged_profile


async def _move_profile_events_and_sessions(duplicate_profiles: List[Profile], merged_profile: Profile):
    for old_profile in duplicate_profiles:
        if old_profile.id != merged_profile.id:
            await raw_db.update_profile_ids('event', old_profile.id, merged_profile.id)
            await event_db.refresh()
            await raw_db.update_profile_ids('session', old_profile.id, merged_profile.id)
            await session_db.refresh()


async def _save_profile(profile):
    # Save in cache
    save_profile_cache(profile)

    # Save to database
    await save_profile(profile)


async def _delete_by_id(profile_id, index):
    # Delete from database
    await delete_profile(profile_id, index)
    # Delete from cache
    delete_profile_cache(profile_id, get_context())


async def _delete_profiles(profile_ids: List[Tuple[str, RecordMetadata]]):
    tasks = [asyncio.create_task(_delete_by_id(profile_id, metadata.index))
             for profile_id, metadata in profile_ids]
    return await asyncio.gather(*tasks)


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
                                   conflict_aux_key: str = "conflicts",
                                   condition:str ='must',
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

            similar_profiles = await profile_db.load_profiles_to_merge(
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

            return await ProfileMerger.compute_one_profile(profile, similar_profiles, conflict_aux_key)

        return None

    @staticmethod
    def _get_merge_key_values(profile: Profile) -> List[tuple]:
        converter = DotNotationConverter(profile)
        values = [converter.get_profile_file_value_pair(key) for key in profile.operation.merge]
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

    def _merge_traits_and_data(self, profiles, merging_strategy: MergingStrategy):
        _traits = [profile.traits for profile in profiles]
        _data = [profile.data.model_dump(mode='json') for profile in profiles]

        old_value = {
            'traits': _traits,
            "data": _data
        }

        new_value = {
            'traits': dict_merge({}, _traits, merging_strategy),
            'data': dict_merge({}, _data, merging_strategy)
        }

        conflicts_aux = get_conflicted_values(old_value, new_value)

        traits = new_value['traits']
        data = ProfileData(**new_value['data'])

        return traits, data, conflicts_aux

    def _get_merged_profile(self,
                            similar_profiles: List[Profile],
                            merging_strategy: MergingStrategy,
                            conflict_aux_key: str = "conflicts",
                            merge_stats: bool = True,
                            merge_time: bool = True
                            ) -> Profile:

        all_profiles = [self.current_profile] + similar_profiles

        # Merge traits and piis

        traits, data, conflicts_aux = self._merge_traits_and_data(all_profiles, merging_strategy)

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

        self.current_profile.aux[conflict_aux_key] = conflicts_aux

        profile = Profile(
            metadata=ProfileMetadata(time=time),
            id=self.current_profile.id,
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

        return profile

    async def merge(self,
                    similar_profiles: List[Profile],
                    conflict_aux_key: str = "conflicts") -> Tuple[Optional[Profile], List[Profile]]:
        return await self._merge(
            similar_profiles,
            allow_duplicate_ids=False,
            conflict_aux_key=conflict_aux_key
        )

    async def deduplicate(self,
                          similar_profiles: List[Profile],
                          conflict_aux_key: str = "conflicts"
                          ) -> Tuple[Optional[Profile], List[Profile]]:
        return await self._merge(
            similar_profiles,
            allow_duplicate_ids=True,
            conflict_aux_key=conflict_aux_key
        )

    async def _merge(self,
                     similar_profiles: List[Profile],
                     allow_duplicate_ids: bool = False,
                     conflict_aux_key: str = "conflicts") -> Tuple[Optional[Profile], List[Profile]]:
        """
        Merges profiles on keys set in profile.operation.merge. Loads profiles from database and
        combines its data into current profile. Returns Profiles object with profiles to be disables.
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
                merging_strategy,
                conflict_aux_key=conflict_aux_key)

            # merged_profile.ids += profiles_to_merge

        return merged_profile, profiles_to_merge

    @staticmethod
    async def compute_one_profile(profile: Optional[Profile], similar_profiles: List[Profile],
                                  conflict_aux_key: str = "conflicts"):

        merger = ProfileMerger(profile)

        # Merge
        merged_profile, duplicate_profiles = await merger.merge(
            similar_profiles,
            conflict_aux_key=conflict_aux_key)

        if merged_profile:
            # Copy ids
            merged_profile = await _copy_duplicated_profiles_ids_to_merged_profile_ids(
                merged_profile,
                duplicate_profiles)

            await _save_profile(merged_profile)

            # Schedule - move events from duplicated profiles
            await _move_profile_events_and_sessions(duplicate_profiles, merged_profile)

            # Schedule - mark duplicated profiles
            records_to_delete: List[Tuple[str, RecordMetadata]] = [(profile.id, profile.get_meta_data())
                                                                   for profile in duplicate_profiles]

            logger.info(f"Profiles to delete {records_to_delete}.")

            await _delete_profiles(records_to_delete)

            # Replace current profile with merged profile
            profile.replace(merged_profile)

            return profile

        else:
            logger.info("No need to merge")

        return None
