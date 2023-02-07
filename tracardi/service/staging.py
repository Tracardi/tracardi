import logging

from tracardi.exceptions.log_handler import log_handler

from tracardi.config import tracardi
from tracardi.service.storage.driver import storage
from tracardi.service.storage.index import resources

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


def get_staged_indices():
    for name, index in resources.resources.items():
        if index.staging:
            stage_index = index.get_single_storage_index()
            stage_alias = index.get_index_alias()
            production_index = index._prefix_with_production(stage_index)
            production_alias = index._prefix_with_production(stage_alias)
            yield stage_index, stage_alias, production_index, production_alias


async def check_if_production_db_exists():
    if tracardi.version.production:
        raise ValueError("Can not deploy in production server.")

    for _, stage_alias, _, production_alias in get_staged_indices():
        if not await storage.driver.raw.exists_alias(production_alias, index=None):
            return False
    return True


async def add_alias_staging_to_production():
    if not await check_if_production_db_exists():
        raise ValueError("Could not find production server data in current database.")

    actions = []
    for stage_index, _, production_index, production_alias in get_staged_indices():
        print(stage_index, production_index, production_alias)
        action = {"add": {"index": stage_index, "alias": production_alias}}
        actions.append(action)
        action = {"remove": {"index": production_index, "alias": production_alias}}
        actions.append(action)
    if actions:
        return await storage.driver.raw.update_aliases({
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
        return await storage.driver.raw.update_aliases({
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
        result = await storage.driver.raw.reindex(source=stage_index, destination=production_index)
        for key in result_sum.keys():
            result_sum = add_up(key, result, result_sum)
        result["index"] = production_index
        results.append(result)
    await remove_alias_staging_to_production()

    return {
        "indices": results,
        "result": result_sum
    }
