import json
import os
from tracardi.config import tracardi, elastic
from tracardi.domain.version import Version
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.setup.setup_plugins import add_plugins
from tracardi.service.storage.driver import storage
from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.index import resources, Index
import logging

__local_dir = os.path.dirname(__file__)

index_mapping = {
    'action': {
        "on-start": add_plugins  # Callable to fill the index
    }
}

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
es = ElasticClient.instance()


async def update_current_version():
    prev_version = await storage.driver.version.load()

    if not prev_version:
        await storage.driver.version.save({"id": 0, **tracardi.version.dict()})
    else:
        prev_version = Version(**prev_version)
        head_version = tracardi.version.get_head_with_prev_version(prev_version)

        if head_version != prev_version:
            await storage.driver.version.save({"id": 0, **head_version.dict()})
            logger.info(f"Saved current version {head_version}")


async def create_indices():

    output = {
        "templates": [],
        "indices": [],
        "aliases": [],
    }

    def add_prefix(json_map, index: Index):
        json_map = json_map.replace("%%PREFIX%%", tracardi.version.name)
        json_map = json_map.replace("%%ALIAS%%", index.get_index_alias())
        json_map = json_map.replace("%%VERSION%%", tracardi.version.get_version_prefix())
        json_map = json_map.replace("%%REPLICAS%%", elastic.replicas)
        json_map = json_map.replace("%%SHARDS%%", elastic.shards)
        return json_map

    def acknowledged(result):
        return 'acknowledged' in result and result['acknowledged'] is True

    async def remove_alias(alias_index):
        if await es.exists_alias(alias_index, index=None):
            result = await es.delete_alias(alias=alias_index, index="_all")
            if acknowledged(result):
                logger.info(f"{alias_index} - DELETED old alias {alias_index}. New will be created", result)
                return True
        return False

    for key, index in resources.resources.items():  # type: str, Index

        if index.mapping:
            map_file = index.mapping
        else:
            map_file = 'mappings/default-dynamic-index.json'

        with open(os.path.join(__local_dir, map_file)) as file:

            map = file.read()
            map = add_prefix(map, index)
            map = json.loads(map)

            target_index = index.get_aliased_data_index()
            alias_index = index.get_index_alias()

            # -------- TEMPLATE --------

            if index.multi_index is True:

                # Remove alias with all indexes first
                await remove_alias(alias_index)

                template_name = index.get_prefixed_template_name()

                # if template exists it must be deleted. Only one template can be per index.

                if await es.exists_index_template(template_name):
                    result = await es.delete_index_template(template_name)
                    if not acknowledged(result):
                        raise ConnectionError(f"Can NOT DELETE template {template_name}.")
                    logger.info(f"{alias_index} - DELETED template {template_name}.")

                # Multi indices need templates. Index will be create automatically on first insert
                result = await es.put_index_template(template_name, map)

                if not acknowledged(result):
                    raise ConnectionError(
                        "Could not create the template `{}`. Received result: {}".format(
                            template_name,
                            result),
                    )

                logger.info(
                    f"{alias_index} - CREATED template `{template_name}` with alias `{alias_index}`. "
                    f"Mapping from `{map_file}` was used. The index will be auto created from template."
                )

            # -------- INDEX --------

            if index.aliased is False:
                target_index = index.get_index_alias()

            if not await es.exists_index(target_index):

                # Creates index and alias in one shot.

                mapping = map['template'] if index.multi_index else map
                result = await es.create_index(target_index, mapping)

                if not acknowledged(result):
                    # Index not created

                    raise ConnectionError(
                        f"Index `{target_index}` was NOT CREATED. The following result was returned: {result}"
                    )

                logger.info(f"{alias_index} - CREATED New index `{target_index}` with alias `{alias_index}`. "
                            f"Mapping from `{map_file}` was used.")

                output['indices'].append(target_index)

            else:
                logger.info(f"{alias_index} - EXISTS Index `{target_index}`.")

    # Recreate all aliases

    actions = []

    for key, index in resources.resources.items():
        if index.aliased:

            alias_index = index.get_index_alias()

            actions.append({"remove": {"index": "_all", "alias": alias_index}})
            if index.multi_index:
                target_index = index.get_template_pattern()
            else:
                target_index = index.get_aliased_data_index()

            actions.append({"add": {"index": target_index, "alias": alias_index}})

    if actions:
        result = await es.update_aliases({
            "actions": actions
        })
        if acknowledged(result):
            logger.info(f"{alias_index} - RECREATED aliases.")
        else:
            raise ConnectionError(f"{alias_index} - Could not recreate aliases.")

    # Check aliases

    for key, index in resources.resources.items():

        # After creating index recreate alias
        if index.aliased:

            target_index = index.get_aliased_data_index()
            alias_index = index.get_index_alias()

            # Check if alias created

            if not await es.exists_alias(alias_index):
                raise ConnectionError(f"Could not recreate alias `{alias_index}` for index `{target_index}`")

            output["aliases"].append(alias_index)

        # -------- SETUP --------

        if key in index_mapping and 'on-start' in index_mapping[key]:
            if index_mapping[key]['on-start'] is not None:
                logger.info(f"{alias_index} - Running on start for index `{key}`.")
                on_start = index_mapping[key]['on-start']
                if callable(on_start):
                    await on_start()

    return output
