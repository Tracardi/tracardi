from tracardi.service.storage.factory import storage_manager


async def load(profile_id, limit):
    result = await storage_manager("profile-purchase").load_by("profile.id",
                                                               profile_id,
                                                               limit if 0 < limit < 1000 else 10)

    return result.dict()
