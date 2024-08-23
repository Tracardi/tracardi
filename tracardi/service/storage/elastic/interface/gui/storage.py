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


async def remove_alias(alias_index):
    return await raw_db.remove_alias(alias_index)


async def reindex(source, destination, wait_for_completion):
    await raw_db.reindex(source, destination, wait_for_completion)


async def health():
    return await raw_db.health()


async def list_indices():
    return await raw_db.indices()


async def remove_template(template_name):
    return raw_db.remove_template(template_name)
