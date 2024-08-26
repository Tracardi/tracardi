from typing import List

from tracardi.service.storage.elastic.dal import profile as profile_dao
from tracardi.service.storage.elastic.dal.event import aggregate_events_by_profile_and_field


async def profile_count() :
    return await profile_dao.count()


async def count_profile_duplicates(profile_ids: List[str]) -> int:
    result = await profile_dao.count_profile_duplicates(profile_ids)
    return result.get("count", 0)


async def load_modified_top_profiles(size) -> dict:
    result = await profile_dao._load_modified_top_profiles(size)
    return result.dict()


async def load_events_by_profile_and_field(profile_id: str, field: str, table: bool = False):
    bucket_name = f"by_{field}"
    result = await aggregate_events_by_profile_and_field(profile_id,
                                                         field=field,
                                                         bucket_name=bucket_name)

    if table:
        return {id: count for id, count in result.aggregations[bucket_name][0].items()}
    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def profile_refresh():
    return await profile_dao.refresh()


async def profile_flush():
    return await profile_dao.flush()
