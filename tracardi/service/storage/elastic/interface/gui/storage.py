from tracardi.domain.query_result import QueryResult
from tracardi.service.storage.elastic.dal.indices_manager import check_indices_mappings_consistency
from tracardi.service.storage.elastic.dal import raw as raw_db


async def get_indices_mappings_consistency() -> dict:
    return await check_indices_mappings_consistency()


async def load_index_mapping_metadata(index: str, filter: str = None) -> QueryResult:
    """
    Returns metadata of given index (str)
    """

    result = await raw_db.get_mapping_fields(index)
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
