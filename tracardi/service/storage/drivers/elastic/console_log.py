from tracardi.service.storage.factory import storage_manager


async def load_by_profile(profile_id: str):
    return await storage_manager('console-log').load_by("profile_id", profile_id)


async def load_by_event(event_id: str):
    return await storage_manager('console-log').load_by("event_id", event_id)
