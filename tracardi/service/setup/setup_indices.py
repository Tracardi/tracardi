import json
import os
from typing import List, Tuple, Generator, Any

from elasticsearch.exceptions import ConnectionTimeout, TransportError

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.plugin.plugin_install import install_default_plugins
from tracardi.service.setup.data.defaults import default_db_data
from tracardi.service.storage.driver.elastic import raw as raw_db
from tracardi.service.storage.index import Resource, Index
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


def acknowledged(result):
    return 'acknowledged' in result and result['acknowledged'] is True


def add_ids(data):
    for record in data:
        record['_id'] = record['id']
        yield record


async def install_default_data():
    for index_name, data in default_db_data.items():
        index = Resource().get_index_constant(index_name)
        await raw_db.bulk_upsert(index.get_write_index(), list(add_ids(data)))


# todo add to install
async def update_mappings():
    for key, index in Resource().resources.items():
        path = f"{__local_dir}/mappings/updates/{key}.json"
        if os.path.isfile(path):
            with open(path) as f:
                update_mappings = json.load(f)
                if index.multi_index:
                    current_indices = await raw_db.indices(index.get_templated_index_pattern())
                    for idx, idx_data in current_indices.items():
                        from pprint import pprint
                        pprint(await raw_db.set_mapping(idx, update_mappings))
                        pprint(await raw_db.get_mapping(idx))


async def create_index_and_template(index, index_map, update_mapping) -> Tuple[List[str], List[str], List[str]]:
    indices_created = []
    templates_created = []
    aliases_created = []

    target_index = index.get_write_index()
    alias_index = index.get_index_alias()

    # -------- TEMPLATE --------

    if index.multi_index is True:

        template_name = index.get_prefixed_template_name()

        if not await raw_db.exists_template(template_name):
            # Multi indices need templates. Index will be created automatically on first insert
            ack, result = await raw_db.add_template(template_name, index_map)

            if not ack:
                raise ConnectionError(
                    "Could not create the template `{}`. Received result: {}".format(
                        template_name,
                        result),
                )

            logger.info(
                f"{alias_index} - CREATED template `{template_name}` with alias `{alias_index}`. "
                f"Mapping from `{index.get_mapping()}` was used. The index will be auto created from template."
            )

            templates_created.append(template_name)

    # -------- INDEX --------

    if not await raw_db.exists_index(target_index):

        # There is no index but the alias may exist
        exists_index_with_alias_name = await raw_db.exists_index(alias_index)

        # Skip this error if the index is static. With static indexes there must be one alias to two indices.
        if not index.static:
            if exists_index_with_alias_name:
                message = f"Could not create index `{target_index}` because the alias `{alias_index}` exists " \
                          f"and points to other index or there is an index name with the same name as the alias."
                logger.error(message)
                raise ConnectionError(message)

        # Creates index and alias in one shot.

        mapping = index_map['template'] if index.multi_index else index_map

        result = None
        for attempt in range(0, 3):
            try:
                result = await raw_db.create_index(target_index, mapping)
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
                    f"Mapping from `{index.get_mapping()}` was used.")

        indices_created.append(target_index)

    else:
        # Always update mappings but raise an error if there is an error
        try:
            logger.info(f"{alias_index} - EXISTS Index `{target_index}`. Updating mapping only.")
            mapping = index_map['template'] if index.multi_index else index_map
            update_result = await raw_db.set_mapping(target_index, mapping['mappings'])
            logger.info(f"{alias_index} - Mapping of `{target_index}` updated. Response {update_result}.")
        except TransportError as e:
            message = f"Update of index {target_index} mapping failed with error {repr(e)}"
            if update_mapping is True:
                raise ConnectionAbortedError(message)
            else:
                logger.error(message)

    # Check if alias exists
    if not await raw_db.exists_alias(alias_index, index=None):
        # Check if it points to target index
        existing_aliases_setup = await raw_db.get_alias(alias_index)
        if target_index not in existing_aliases_setup:

            result = await raw_db.update_aliases({
                "actions": [{"add": {"index": target_index, "alias": alias_index}}]
            })
            if acknowledged(result):
                logger.info(f"CREATED alias {alias_index} to target index {target_index}.")
            else:
                raise ConnectionError(f"Could not create alias {alias_index} to target index {target_index}.")

            aliases_created.append(alias_index)

    return indices_created, templates_created, aliases_created


async def run_on_start():
    for key, _ in Resource().resources.items():
        if key in index_mapping and 'on-start' in index_mapping[key]:
            if index_mapping[key]['on-start'] is not None:
                logger.info(f"Running on start for index `{key}`.")
                on_start = index_mapping[key]['on-start']
                if callable(on_start):
                    await on_start()


async def create_schema(index_mappings: Generator[Tuple[Index, dict], Any, None], update_mapping: bool = False):
    output = {
        "templates": [],
        "indices": [],
        "aliases": [],
    }

    for index, map in index_mappings:
        created_indices, created_templates, create_aliases = await create_index_and_template(
            index,
            map,
            update_mapping)

        output['indices'] += created_indices
        output['templates'] += created_templates
        output['aliases'] += create_aliases

    return output

# def get_index(index, mapping_file, version):
#     if 'name' in index:
#         del index['name']
#     index['mapping'] = mapping_file
#     index = Index(**index)
#     index.set_version(version)
#
#     return index
#
# async def remote_system_upgrade(version):
#     def get_index_mappings(version) -> Generator[Tuple[Index, dict], Any, None]:
#         for mapping_file, index in data['indices'].items():
#
#             index = get_index(index, mapping_file, version)
#
#             if mapping_file not in data['mappings']:
#                 raise ValueError(f"No mapping for {index.index} in release settings for version {version}.")
#             mapping = index.prepare_mappings(data['mappings'][mapping_file], index)
#
#             yield index, mapping
#
#     async with HttpClient(3, 200) as client:
#         async with client.get(f"http://localhost:11111/{version}", json={}) as response:
#             data = await response.json()
#             if 'mappings' not in data:
#                 raise ValueError(f"No mappings in release settings for version {version}.")
#
#             if 'indices' not in data:
#                 raise ValueError(f"No indices in release settings for version {version}.")
#
#             # Install
#             with ServerContext(get_context().switch_context(production=True)):
#                 await create_schema(get_index_mappings(version), update_mapping=False)
#                 await install_default_data(version)
#
#             with ServerContext(get_context().switch_context(production=False)):
#                 await create_schema(get_index_mappings(version), update_mapping=False)
#                 await install_default_data(version)
#
#
# if __name__ == "__main__":
#     import asyncio
#
#     asyncio.run(remote_system_upgrade('1.0.0'))
