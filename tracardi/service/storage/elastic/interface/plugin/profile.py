from tracardi.service.storage.elastic.dal.profile import _load_active_profile_by_field


async def load_active_profile_by_field(field: str, value: str, start: int = 0, limit: int = 100):
    return _load_active_profile_by_field(field, value, start, limit)
