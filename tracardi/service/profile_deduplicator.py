from tracardi.domain.profile import Profile
from tracardi.domain.storage_record import StorageRecord, RecordMetadata
from tracardi.service.profile_merger import ProfileMerger
from tracardi.service.storage.factory import storage_manager


async def _load_duplicates(id: str):
    return await storage_manager('profile').query({
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            "ids": id
                        }
                    },
                    {
                        "term": {
                            "id": id
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    })


async def deduplicate_profile(profile_id):
    _duplicated_profiles = await _load_duplicates(profile_id)  # 1st records is the newest
    valid_profile_record = _duplicated_profiles.first()  # type: StorageRecord
    first_profile = valid_profile_record.to_entity(Profile)

    if len(_duplicated_profiles) == 1:
        # If 1 then there is no duplication
        return first_profile

    # Create empty profile where we will merge duplicates
    profile = Profile.new()
    profile.set_meta_data(RecordMetadata(id=profile_id, index=profile.get_meta_data().index))

    similar_profiles = []
    for _profile_record in _duplicated_profiles:
        similar_profiles.append(_profile_record.to_entity(Profile))

    merger = ProfileMerger(profile)
    return await merger.compute_one_profile(profile, similar_profiles)
