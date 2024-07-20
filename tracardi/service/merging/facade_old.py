from typing import List, Optional

from tracardi.domain.profile import Profile
from tracardi.service.profile_merger import ProfileMerger
from tracardi.service.storage.elastic.interface.collector.mutation import profile as mutation_profile_db

from tracardi.service.storage.elastic.interface import profile as profile_db
from tracardi.domain.storage_record import RecordMetadata


async def merge_profile_by_merging_keys(profile: Optional[Profile], merge_by) -> Optional[Profile]:
    return await ProfileMerger.invoke_merge_profile(
        profile,
        # Merge when id = tracker_payload.profile.id
        # This basically loads the current profile.
        merge_by=merge_by,
        limit=2000)


def get_merging_keys_and_values(profile: Profile):
    return ProfileMerger.get_merging_keys_and_values(profile)


def first(items) -> Optional[Profile]:
    if len(items) > 0:
        return items[0]
    return None


async def deduplicate_profile(profile_id: str, profile_ids: List[str] = None) -> Optional[Profile]:
    if isinstance(profile_ids, list):
        set(profile_ids).add(profile_id)
        profile_ids = list(profile_ids)
    else:
        profile_ids = [profile_id]

    _duplicated_profiles = await profile_db.load_profile_duplicates(profile_ids)  # 1st records is the newest
    first_profile = first(_duplicated_profiles)  # type: Profile
    if first_profile is None:
        raise ValueError("Could not fetch first profile. Probably already merged.")

    if len(_duplicated_profiles) == 1:
        if first_profile.metadata.system.has_merging_data():
            first_profile.metadata.system.remove_merging_data()
            first_profile.mark_for_update()
            await mutation_profile_db.save_profile(first_profile, refresh=True)

        # If 1 then there is no duplication
        return first_profile

    # Create empty profile where we will merge duplicates
    profile = Profile.new()
    profile.set_meta_data(RecordMetadata(id=profile_id, index=profile.get_meta_data().index))

    # Merged profiles refresh index
    return await ProfileMerger(profile).compute_one_profile(_duplicated_profiles)
