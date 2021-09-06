from tracardi.domain.profile import Profile
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

from tracardi.service.storage.factory import StorageFor


async def save_profile(profile: Profile, persist_profile: bool = True):
    if persist_profile and profile.operation.new:
        return await StorageFor(profile).index().save()
    else:
        return BulkInsertResult()
