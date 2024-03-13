from typing import List
from tracardi.domain.profile import Profile
from tracardi.domain.storage_record import StorageRecord, RecordMetadata
from tracardi.service.profile_merger import ProfileMerger
from tracardi.service.tracking.storage.profile_storage import save_profile
from tracardi.service.storage.driver.elastic import profile as profile_db

async def deduplicate_profile(profile_id: str, profile_ids:List[str] = None):

    if isinstance(profile_ids, list):
        set(profile_ids).add(profile_id)
        profile_ids = list(profile_ids)
    else:
        profile_ids = [profile_id]

    _duplicated_profiles = await profile_db.load_profile_duplicates(profile_ids)  # 1st records is the newest
    valid_profile_record = _duplicated_profiles.first()  # type: StorageRecord
    if valid_profile_record is None:
        raise ValueError("Could not fetch first profile. Probably already merged.")
    first_profile = valid_profile_record.to_entity(Profile)

    if len(_duplicated_profiles) == 1:
        if first_profile.metadata.system.has_merging_data():
            first_profile.metadata.system.remove_merging_data()
            first_profile.mark_for_update()
            await save_profile(first_profile, refresh=True)

        # If 1 then there is no duplication
        return first_profile

    # Create empty profile where we will merge duplicates
    profile = Profile.new()
    profile.set_meta_data(RecordMetadata(id=profile_id, index=profile.get_meta_data().index))

    similar_profiles = []
    for _profile_record in _duplicated_profiles:
        similar_profiles.append(_profile_record.to_entity(Profile))

    # Merged profiles refresh index
    merger = ProfileMerger(profile)
    return await merger.compute_one_profile(similar_profiles)
