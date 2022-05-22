import json
import os

from tracardi.config import tracardi, elastic
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


async def create_indices():

    output = {
        "templates": [],
        "indices": [],
        "aliases": [],
    }

    def add_prefix(mapping, index: Index):
        json_map = json.dumps(mapping)

        json_map = json_map.replace("%%PREFIX%%-", f"{elastic.instance_prefix}-")
        json_map = json_map.replace("%%ALIAS%%", index.get_read_index())
        json_map = json_map.replace("%%VERSION%%", tracardi.version.get_version_prefix())

        return json.loads(json_map)

    def acknowledged(result):
        return 'acknowledged' in result and result['acknowledged'] is True

    async def remove_alias(alias_index):
        if await es.exists_alias(alias_index, index=None):
            result = await es.delete_alias(alias=alias_index, index="_all")
            if acknowledged(result):
                logger.info(f"{alias_index} - Deleted old alias {alias_index}. New will be created", result)
                return True
        return False

    async def recreate_one_alias(alias_index, target_index):
        result = await es.recreate_one_alias(alias=alias_index, index=target_index)
        if acknowledged(result):
            logger.info(f"{alias_index} - RECREATED alias {alias_index} for target `{target_index}` created.")
        else:
            raise ConnectionError(f"{alias_index} - Could not recreate alias {alias_index}")

    for key, index in resources.resources.items():  # type: str, Index

        if index.mapping:
            map_file = index.mapping
        else:
            map_file = 'mappings/default-dynamic-index.json'

        with open(os.path.join(__local_dir, map_file)) as file:

            map = json.load(file)
            map = add_prefix(map, index)

            target_index = index.get_aliased_data_index()
            alias_index = index.get_read_index()

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
                    f"{alias_index} - The index template `{template_name}` with alias `{alias_index}` created. "
                    f"Mapping from `{map_file}` was used. The index will be auto created from template."
                )

                # Create first empty index if not exists

                if not await es.exists_index(target_index):
                    result = await es.create_index(target_index, map['template'])
                    if not acknowledged(result):
                        raise ConnectionError(f"Could not create index {target_index}.")
                    logger.info(
                            f"{alias_index} - Empty index `{target_index}` with alias `{alias_index}` created. "
                        )
                else:
                    logger.info(f"{alias_index} - Index `{target_index}` already exists.")

                output["templates"].append(target_index)

            else:

                target_index_exists = await es.exists_index(target_index)
                alias_exists = await storage.driver.raw.exists_alias(index=target_index, alias=alias_index)

                # todo what if index exists but alias not, or alias exists but index not
                if not target_index_exists and not alias_exists:

                    # todo Error may occur
                    """
                        ERROR:app.setup.indices_setup:New index `tracardi-flow-action-plugins` was not created. The 
                        following result was returned {'error': {'root_cause': [{'type': 'resource_already_exists_exception'
                        , 'reason': 'index [tracardi-flow-action-plugins/fk4wGYqeROCd9Cp5vtfnaw] already exists', 
                        'index_uuid': 'fk4wGYqeROCd9Cp5vtfnaw', 'index': 'tracardi-flow-action-plugins'}], 'type': 
                        'resource_already_exists_exception', 'reason': 
                        'index [tracardi-flow-action-plugins/fk4wGYqeROCd9Cp5vtfnaw] already exists', 'index_uuid': 
                        'fk4wGYqeROCd9Cp5vtfnaw', 'index': 'tracardi-flow-action-plugins'}, 'status': 400}
                    """

                    # Creates index and alias in one shot.

                    result = await es.create_index(target_index, map)

                    if not acknowledged(result):
                        # Index not created

                        raise ConnectionError(
                            "Index {} `{}` was NOT CREATED. The following result was returned {}".format(
                                'template' if index.multi_index else 'index',
                                target_index,
                                result)
                        )

                    logger.info(f"{alias_index} - New {'template' if index.multi_index else 'index'} `{target_index}` "
                                f"created with alias `{alias_index}`. Mapping from `{map_file}` was used.")

                    if key in index_mapping and 'on-start' in index_mapping[key]:
                        if index_mapping[key]['on-start'] is not None:
                            logger.info(f"{alias_index} - Running on start for index `{key}`.")
                            on_start = index_mapping[key]['on-start']
                            if callable(on_start):
                                await on_start()

                    output['indices'].append(target_index)

                else:
                    logger.info(f"{alias_index} - Index `{target_index}` exists.")

            # After creating index recreate alias

            await recreate_one_alias(alias_index, target_index)

            # Check if alias created

            if not await es.exists_alias(alias_index):
                raise ConnectionError(f"Could not recreate alias `{alias_index}` for index `{target_index}`")

            output["aliases"].append(alias_index)

    return output
