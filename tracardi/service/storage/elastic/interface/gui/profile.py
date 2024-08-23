from typing import List

from tracardi.service.storage.elastic.dal import profile as profile_db


async def profile_count():
    return await profile_db.count()


async def count_profile_duplicates(profile_ids: List[str]) -> int:
    result = await profile_db.count_profile_duplicates(profile_ids)
    return result.get("count", 0)
