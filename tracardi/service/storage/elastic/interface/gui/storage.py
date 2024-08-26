from tracardi.domain.query_result import QueryResult
from tracardi.domain.time_range_query import DatetimeRangePayload
from tracardi.service.storage.elastic.dal.indices_manager import check_indices_mappings_consistency
from tracardi.service.storage.elastic.dal import raw as raw_db


async def get_indices_mappings_consistency() -> dict:
    return await check_indices_mappings_consistency()


async def load_mapping_fields(index: str):
    return await raw_db.get_mapping_fields(index)


async def load_index_mapping_metadata(index: str, filter: str = None) -> QueryResult:
    """
    Returns metadata of given index (str)
    """

    result = await load_mapping_fields(index)
    if filter is not None:
        result = [item for item in result if item.startswith(filter) and item != filter]
    return QueryResult(result=result, total=len(result))


async def remove_index(index_name: str):
    return await raw_db.remove_index(index_name)


async def exists_index(index_name: str):
    return await raw_db.exists_index(index_name)


async def load_alias(alias_index: str):
    return await raw_db.get_alias(alias_index)


async def remove_alias(alias_index):
    return await raw_db.remove_alias(alias_index)


async def update_aliases(target_index: str, alias_index: str):
    return await raw_db.update_aliases({
        "actions": [{"add": {"index": target_index, "alias": alias_index}}]
    })


async def exists_alias(alias_index: str, target_index: str):
    return await raw_db.exists_alias(alias_index, index=target_index)


async def reindex(source, destination, wait_for_completion):
    await raw_db.reindex(source, destination, wait_for_completion)


async def health():
    return await raw_db.health()


async def list_indices(index_pattern="*"):
    """
    This one returns raw data as it is elastic specific.
    """
    return await raw_db.indices(index_pattern)


async def remove_template(template_name):
    return raw_db.remove_template(template_name)


async def exists_template(template_name: str):
    return await raw_db.exists_template(template_name)


async def save_template(template_name, index_map):
    return await raw_db.add_template(template_name, index_map)


async def create_index(index: str, mapping: dict):
    return await raw_db.create_index(index, mapping)


async def load_task_status(task_id: str):
    """
    This one returns raw data as it is elastic specific.
    """
    return await raw_db.task_status(task_id)


async def load_mapping(index: str):
    """
    This one returns raw data as it is elastic specific.
    """
    return await raw_db.get_mapping(index)


async def save_mapping(idx, update_mappings):
    return await raw_db.set_mapping(idx, update_mappings)


async def count(index: str, query: dict = None):
    return await raw_db.count(index, query)


async def refresh(index:str):
    return await raw_db.refresh(index)


async def flush(index: str):
    return await raw_db.flush(index)


async def query_by_index(index, query):
    return await raw_db.query_by_index(
        index=index,
        query=query
    )


async def count_by_query(index, query, time_span):
    return await raw_db.count_by_query(
        index=index,
        query=query,
        time_span=time_span
    )


async def load_unique_field_values(index: str, field: str):
    return await raw_db.get_unique_field_values(index, field)


async def query_by_sql(index: str, query: str, start: int = 0, limit: int = 0):
    return await raw_db.get_unique_field_values(index, query, start, limit)


async def query_by_sql_in_time_range(index: str, query: DatetimeRangePayload) -> QueryResult:
    return await raw_db.query_by_sql_in_time_range(index, query)


async def histogram_by_sql_in_time_range(index, query: DatetimeRangePayload, group_by: str = None) -> QueryResult:
    return await raw_db.histogram_by_sql_in_time_range(index, query, group_by)


def count_all_indices_by_alias():
    return raw_db.count_all_indices_by_alias()


async def update_profile_ids(index: str, old_profile_id: str, merged_profile_id):
    return await raw_db.update_profile_ids(index, old_profile_id, merged_profile_id)
