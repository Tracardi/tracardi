import asyncio
from asyncio import Task
from collections import defaultdict
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any
from pydantic.utils import deep_update, KeyType

from ..domain.metadata import ProfileMetadata
from ..domain.profile import Profile
from ..domain.profile_stats import ProfileStats
from ..domain.time import ProfileTime
from ..service.dot_notation_converter import DotNotationConverter

from tracardi.service.merger import merge as dict_merge
from ..service.storage.driver import storage


class ProfileMerger:

    def __init__(self, profile: Profile):
        self.current_profile = profile

    @staticmethod
    def _save_duplicate_profiles(duplicate_profiles: List[Profile]):
        profile_by_index = defaultdict(list)
        for dup_profile in duplicate_profiles:
            profile_by_index[dup_profile.get_meta_data().index].append(dup_profile)

        save_tasks = []
        for _, profile_bulk in profile_by_index.items():
            task = asyncio.create_task(
                storage.driver.profile.save_all(profile_bulk)
            )
            save_tasks.append(task)
        return save_tasks

    @staticmethod
    def _move_events(profile: Profile) -> List[Task]:
        storage.driver.event.update_tags()
        # TODO Save - move events
        return []

    @staticmethod
    async def invoke_merge_profile(profile: Optional[Profile],
                                   merge_by: List[Tuple[str, str]],
                                   override_old_data: bool = True,
                                   limit: int = 2000) -> Optional[Tuple[Profile, List[Task]]]:
        if len(merge_by) > 0:
            # Load all profiles that match merging criteria
            similar_profiles = await storage.driver.profile.load_profiles_to_merge(
                merge_by,
                limit=limit
            )

            merger = ProfileMerger(profile)

            # Merge
            merged_profile, duplicate_profiles = await merger.merge(
                similar_profiles,
                override_old_data=override_old_data)

            if merged_profile:

                # Replace current profile with merged profile
                profile.replace(merged_profile)

                # Update profile after merge
                profile.operation.update = True

                # Schedule - mark duplicated profiles
                save_tasks = ProfileMerger._save_duplicate_profiles(duplicate_profiles)
                # Schedule - move events from duplicated profiles
                save_tasks += ProfileMerger._move_events(profile)

                return profile, save_tasks

        return None

    @staticmethod
    def _get_merge_key_values(profile: Profile) -> List[tuple]:
        converter = DotNotationConverter(profile)
        return [converter.get_profile_file_value_pair(key) for key in profile.operation.merge]

    @staticmethod
    def get_merging_keys_and_values(profile: Profile) -> List[Tuple[str, str]]:
        merge_key_values = ProfileMerger._get_merge_key_values(profile)

        # Add keyword
        merge_key_values = [(field, value) for field, value in merge_key_values if value is not None]

        return merge_key_values

    @staticmethod
    def _mark_profiles_as_merged(profiles: List[Profile], merge_with: str) -> List[Profile]:
        disabled_profiles = []

        for profile in profiles:
            profile.active = False
            profile.metadata.merged_with = merge_with
            disabled_profiles.append(profile)

        return disabled_profiles

    @staticmethod
    def _deep_update(mapping: Dict[KeyType, Any], *updating_mappings: Dict[KeyType, Any]) -> Dict[KeyType, Any]:
        updated_mapping = mapping.copy()
        for updating_mapping in updating_mappings:
            for k, v in updating_mapping.items():
                if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                    updated_mapping[k] = deep_update(updated_mapping[k], v)
                elif v is not None:
                    updated_mapping[k] = v
        return updated_mapping

    def _get_merged_profile(self,
                            similar_profiles: List[Profile],
                            override_old_data=True) -> Profile:

        all_profiles = similar_profiles + [self.current_profile]

        # Merge traits and piis

        if override_old_data is False:

            """
                Marge do not loose data. Conflicts are resoled to list of values.
                E.g. Name="bill" + Name="Wiliam"  = Name=['bill','wiliam']
            """

            traits = [profile.traits.dict() for profile in all_profiles]
            piis = [profile.pii.dict() for profile in all_profiles]
            traits = dict_merge({}, traits)
            piis = dict_merge({}, piis)

        else:

            """
                Marge overrides data. Conflicts are resoled to single value. Latest wins.
                E.g. Name="bill" + Name="Wiliam" = Name='wiliam'
            """

            current_profile_dict = self.current_profile.dict()
            # i = 0
            for profile in all_profiles:
                # i += 1
                # if i == 5:
                #     profile.pii.name = "risto"
                #     profile.traits.private['a'] =1
                #
                # if i == 8:
                #     profile.traits.private = {}

                current_profile_dict['traits'] = self._deep_update(current_profile_dict['traits'], profile.traits.dict())
                current_profile_dict['pii'] = self._deep_update(current_profile_dict['pii'], profile.pii.dict())

            traits = current_profile_dict['traits']
            piis = current_profile_dict['pii']

        # Merge stats, consents, segments, etc.

        consents = {}
        segments = []
        interests = {}
        stats = ProfileStats()
        time = ProfileTime(**self.current_profile.metadata.time.dict())

        for profile in all_profiles:  # Type: Profile

            # Time

            time.visit.count += profile.metadata.time.visit.count

            if isinstance(time.visit.current, datetime) and isinstance(profile.metadata.time.visit.current, datetime):
                if time.visit.current < profile.metadata.time.visit.current:
                    time.visit.current = profile.metadata.time.visit.current

            if isinstance(time.visit.last, datetime) and isinstance(profile.metadata.time.visit.last, datetime):
                if time.visit.last < profile.metadata.time.visit.last:
                    time.visit.last = profile.metadata.time.visit.last

            # Stats

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

            for interest, count in profile.interests.items():
                if interest not in interests:
                    interests[interest] = 0
                interests[interest] += profile.interests[interest]

        # Set id to merged id or current profile id.
        id = self.current_profile.metadata.merged_with if self.current_profile.metadata.merged_with is not None else self.current_profile.id

        profile = Profile(
            metadata=ProfileMetadata(time=time),
            id=id,
            stats=stats,
            traits=traits,
            pii=piis,
            segments=segments,
            consents=consents,
            interests=dict(interests),
            active=True
        )

        return profile

    async def merge(self,
                    similar_profiles: List[Profile],
                    override_old_data: bool = True) -> Tuple[Optional[Profile], List[Profile]]:
        """
        Merges profiles on keys set in profile.operation.merge. Loads profiles from database and
        combines its data into current profile. Returns Profiles object with profiles to be disables.
        It does not disable profiles or saves merged profile.
        """

        merged_profile = None
        disabled_profiles = []

        if len(similar_profiles) > 0:

            # Filter only profiles that are not current profile and where not merged
            profiles_to_merge = [p for p in similar_profiles if p.id != self.current_profile.id and p.active is True]

            # Are there any profiles to merge?
            if len(profiles_to_merge) > 0:

                # Add current profile to existing ones and get merged profile

                merged_profile = self._get_merged_profile(
                    profiles_to_merge,
                    override_old_data=override_old_data)

                # Deactivate all other profiles except merged one

                profiles_to_disable = [p for p in similar_profiles if p.id != self.current_profile.id]
                disabled_profiles = self._mark_profiles_as_merged(profiles_to_disable,
                                                                  merge_with=self.current_profile.id)

        return merged_profile, disabled_profiles

    def move_events(self):
        pass
