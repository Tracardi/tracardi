import asyncio

from tracardi.config import tracardi
from tracardi.service.storage.driver import storage
from tracardi.service.storage.index import resources


def get_staged_indices():
    for name, index in resources.resources.items():
        if index.staging:
            stage_index = index.get_single_storage_index()
            stage_alias = index.get_index_alias()
            production_index = f"prod-{stage_index}"
            production_alias = f"prod-{stage_alias}"
            yield stage_index, stage_alias, production_index, production_alias


async def check_if_production_db_exists():
    if tracardi.version.production:
        raise ValueError("Can not deploy in production server.")

    for _, stage_alias, _, production_alias in get_staged_indices():
        if not await storage.driver.raw.exists_alias(production_alias, index=None):
            return False
    return True


async def add_alias_staging_to_production():
    actions = []
    for stage_index, _, _, production_alias in get_staged_indices():
        action = {"add": {"index": stage_index, "alias": production_alias}}
        actions.append(action)
    if actions:
        await storage.driver.raw.update_aliases({
            "actions": actions
        })


async def remove_alias_staging_to_production():
    actions = []
    for stage_index, _, _, production_alias in get_staged_indices():
        action = {"remove": {"index": stage_index, "alias": production_alias}}
        actions.append(action)
    if actions:
        await storage.driver.raw.update_aliases({
            "actions": actions
        })


async def move_from_staging_to_production():
    print(tracardi.version)
    if not await check_if_production_db_exists():
        raise ValueError("Could not find production server data in current database.")

    await add_alias_staging_to_production()

    for stage_index, _, production_index, _ in get_staged_indices():
        print(stage_index, production_index)
        # await storage.driver.raw.reindex(source="", destination="")

    await remove_alias_staging_to_production()
    await remove_alias_staging_to_production()


asyncio.run(move_from_staging_to_production())
