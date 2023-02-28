import json
import os

from elasticsearch.exceptions import ConnectionTimeout
from json import JSONDecodeError
from tracardi.config import tracardi
from tracardi.domain.version import Version
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.plugin.plugin_install import install_default_plugins
from tracardi.service.setup.data.defaults import default_db_data
from tracardi.service.storage.driver import storage
from tracardi.service.storage.index import resources, Index
import logging

__local_dir = os.path.dirname(__file__)

index_mapping = {
    'action': {
        "on-start": install_default_plugins  # Callable to fill the index
    }
}

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


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


async def install_default_data():
    for index, data in default_db_data.items():
        for record in data:
            await storage.driver.raw.index(index).upsert(record)


async def create_indices():

    output = {
        "templates": [],
        "indices": [],
        "aliases": [],
    }

    def acknowledged(result):
        return 'acknowledged' in result and result['acknowledged'] is True

    for key, index in resources.resources.items():  # type: str, Index

        map_file = index.get_mapping()

        with open(map_file) as file:

            map = file.read()
            map = index.prepare_mappings(map, index)
            try:
                map = json.loads(map)
            except JSONDecodeError as e:
                logger.error(f"Could not read JSON mapping file {map_file}. error {str(e)}")
                raise e

            target_index = index.get_write_index()
            alias_index = index.get_index_alias()

            # -------- TEMPLATE --------

            if index.multi_index is True:

                # Remove alias with all indexes first
                result = await storage.driver.raw.remove_alias(alias_index)
                if result:
                    logger.info(f"{alias_index} - DELETED old alias {alias_index}. New will be created")

                template_name = index.get_prefixed_template_name()

                # if template exists it must be deleted. Only one template can be per index.

                if not await storage.driver.raw.remove_template(template_name):
                    raise ConnectionError(f"Can NOT DELETE template {template_name}.")

                logger.info(f"{alias_index} - DELETED template {template_name}.")

                # Multi indices need templates. Index will be created automatically on first insert
                result = await storage.driver.raw.add_template(template_name, map)

                if not result:
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

            if not await storage.driver.raw.exists_index(target_index):

                # There is no index but the alias may exist
                exists_index_with_alias_name = await storage.driver.raw.exists_index(alias_index)

                # Skip this error if the index is static. With static indexes there must be one alias to two indices.
                if not index.static:
                    if exists_index_with_alias_name:
                        message = f"Could not create index `{target_index}` because the alias `{alias_index}` exists " \
                                  f"and points to other index or there is an index name with the same name as the alias."
                        logger.error(message)
                        raise ConnectionError(message)

                # Creates index and alias in one shot.

                mapping = map['template'] if index.multi_index else map

                for attempt in range(0, 3):
                    try:
                        print(target_index, mapping)
                        result = await storage.driver.raw.create_index(target_index, mapping)
                        break
                    except ConnectionTimeout as e:
                        raise ConnectionError(
                            f"Index `{target_index}` was NOT CREATED at attempt {attempt} due to an error: {str(e)}"
                        )

                if not result:
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
        alias_index = index.get_index_alias()
        # Do not remove aliases for static indices.
        if not index.static:
            actions.append({"remove": {"index": "_all", "alias": alias_index}})

        if index.multi_index:
            target_index = index.get_templated_index_pattern()
        else:
            target_index = index.get_write_index()

        actions.append({"add": {"index": target_index, "alias": alias_index}})

    if actions:

        result = await storage.driver.raw.update_aliases({
            "actions": actions
        })
        if acknowledged(result):
            logger.info(f"{alias_index} - RECREATED aliases.")
        else:
            raise ConnectionError(f"{alias_index} - Could not recreate aliases.")

    # Check aliases

    for key, index in resources.resources.items():

        # After creating index recreate alias
        target_index = index.get_write_index()
        alias_index = index.get_index_alias()

        # Check if alias created

        if not await storage.driver.raw.exists_alias(alias_index, index=None):
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
