from datetime import datetime
from typing import Optional, List, Tuple

from pydantic.utils import deep_update

from tracardi.domain.metadata import ProfileMetadata
from tracardi.domain.profile import Profile
from tracardi.service.storage.driver import storage
from tracardi.service.merger import merge as dict_merge


class ProfileMerger:

    def __init__(self, profile: Profile):
        self.current_profile = profile

    @staticmethod
    def _mark_profiles_as_merged(profiles: List[Profile], merge_with: str) -> List[Profile]:
        disabled_profiles = []

        for profile in profiles:
            profile.active = False
            profile.metadata.merged_with = merge_with
            disabled_profiles.append(profile)

        return disabled_profiles

    def _get_merged_profile(self, similar_profiles: List[Profile], current_profile: Profile, override_old_data=True) -> Profile:

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
            for profile in all_profiles:
                current_profile_dict['traits'] = deep_update(current_profile_dict['traits'], profile.traits.dict())
                current_profile_dict['pii'] = deep_update(current_profile_dict['pii'], profile.pii.dict())
            traits = current_profile_dict['traits']
            piis = current_profile_dict['pii']

        # Merge stats, consents, segments, etc.

        consents = self.current_profile.consents
        segments = self.current_profile.segments
        interests = self.current_profile.interests
        stats = self.current_profile.stats
        time = self.current_profile.metadata.time
        for profile in all_profiles:  # Type: Profile

            # Time

            # print(profile.metadata.time)
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

        return Profile(
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

    async def merge(self,
                    similar_profiles: List[Profile],
                    override_old_data: bool = True) -> Tuple[Profile, List[Profile]]:
        """
        Merges profiles on keys set in profile.operation.merge. Loads profiles from database and
        combines its data into current profile. Returns Profiles object with profiles to be disables.
        It does not disable profiles or saves merged profile.
        """

        merged_profile = self.current_profile
        disabled_profiles = []

        if len(similar_profiles) > 0:

            # Filter only profiles that are not current profile and where not merged
            profiles_to_merge = [p for p in similar_profiles if p.id != self.current_profile.id and p.active is True]

            # Are there any profiles to merge?
            if len(profiles_to_merge) > 0:
                # Add current profile to existing ones and get merged profile
                merged_profile = self._get_merged_profile(
                    profiles_to_merge,
                    current_profile=self.current_profile,
                    override_old_data=override_old_data)

                # Deactivate all other profiles except merged one

                profiles_to_disable = [p for p in similar_profiles if p.id != self.current_profile.id]
                disabled_profiles = self._mark_profiles_as_merged(profiles_to_disable, merge_with=self.current_profile.id)

                # disabled_profiles = Profiles(disabled_profiles)

                # Replace current profile with merged profile
                # current_profile.replace(merged_profile)

                # Update profile after merge
                merged_profile.operation.update = True

        return merged_profile, disabled_profiles
