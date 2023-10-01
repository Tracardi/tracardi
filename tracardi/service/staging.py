import logging

from tracardi.context import get_context
from tracardi.exceptions.log_handler import log_handler

from tracardi.config import tracardi
from tracardi.service.storage.driver.elastic import raw as raw_db
from tracardi.service.storage.index import Resource

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


def get_staged_indices():
    for name, index in Resource().resources.items():
        if index.staging:
            stage_index = index.get_single_storage_index()
            stage_alias = index.get_index_alias()
            production_index = index._prefix_with_production(stage_index)
            production_alias = index._prefix_with_production(stage_alias)
            yield stage_index, stage_alias, production_index, production_alias


async def check_if_production_db_exists():
    if get_context().is_production():
        raise ValueError("Can not deploy in production server.")

    for _, stage_alias, _, production_alias in get_staged_indices():
        if not await raw_db.exists_alias(production_alias, index=None):
            return False
    return True


async def add_alias_staging_to_production():
    if not await check_if_production_db_exists():
        raise ValueError("Could not find production server data in current database.")

    actions = []
    for stage_index, _, production_index, production_alias in get_staged_indices():
        action = {"add": {"index": stage_index, "alias": production_alias}}
        actions.append(action)
        action = {"remove": {"index": production_index, "alias": production_alias}}
        actions.append(action)
    if actions:
        return await raw_db.update_aliases({
            "actions": actions
        })


async def remove_alias_staging_to_production():
    if not await check_if_production_db_exists():
        raise ValueError("Could not find production server data in current database.")
    actions = []
    for stage_index, _, production_index, production_alias in get_staged_indices():
        action = {"remove": {"index": stage_index, "alias": production_alias}}
        actions.append(action)
        action = {"add": {"index": production_index, "alias": production_alias}}
        actions.append(action)
    if actions:
        return await raw_db.update_aliases({
            "actions": actions
        })


def add_up(key, result, result_sum):
    if key in result:
        result_sum[key] += result[key]
    return result_sum


async def move_from_staging_to_production():
    if not await check_if_production_db_exists():
        raise ValueError("Could not find production server data in current database.")

    await add_alias_staging_to_production()

    result_sum = {
        "took": 0,
        'total': 0,
        'updated': 0,
        'created': 0,
        'deleted': 0,
        'batches': 0,
        'version_conflicts': 0,
        'noops': 0,
        'failures': []
    }
    results = []

    for stage_index, _, production_index, _ in get_staged_indices():
        logger.info(f"Coping data from {stage_index} to {production_index}")
        # Delete data in index
        result = await raw_db.delete_by_query(index=production_index, query={
            "query": {
                "match_all": {}
            }
        })

        logger.info(f"Deleted data from {production_index}, {result.get('deleted', None)}")

        # Refresh
        await raw_db.refresh(index=production_index)

        # Reindex
        result = await raw_db.reindex(source=stage_index, destination=production_index)
        for key in result_sum.keys():
            result_sum = add_up(key, result, result_sum)
        result["index"] = production_index
        results.append(result)
    await remove_alias_staging_to_production()

    return {
        "indices": results,
        "result": result_sum
    }
