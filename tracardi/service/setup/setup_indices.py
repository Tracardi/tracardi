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


async def create_indices():

    def add_prefix(mapping, index: Index):
        json_map = json.dumps(mapping)
        json_map = json_map.replace("%%PREFIX%%-", f"{elastic.instance_prefix}-" if elastic.instance_prefix else "")
        json_map = json_map.replace("%%ALIAS%%", index.get_read_index())
        return json.loads(json_map)

    es = ElasticClient.instance()
    for key, index in resources.resources.items():  # type: str, Index

        if index.mapping:
            map_file = index.mapping
        else:
            map_file = 'mappings/default-dynamic-index.json'

        with open(os.path.join(__local_dir, map_file)) as file:

            map = json.load(file)
            map = add_prefix(map, index)

            target_index = index.get_write_index()
            alias_index = index.get_read_index()

            if index.multi_index is True:

                # Multi indices need templates. Index will be create automatically on first insert
                result = await es.put_index_template(index.get_prefixed_template_name(), map)

                if 'acknowledged' not in result or result['acknowledged'] is not True:
                    logger.error(
                        "Could not create the template for `{}`. Received result: {}".format(
                            target_index,
                            result),
                    )
                    continue

                logger.info(
                    "The template for `{}` index created. Mapping from `{}` was used. The index will be "
                    "auto created from template.".format(
                        target_index,
                        map_file)
                )

                yield "template", target_index, alias_index

            else:

                target_index_exists = await es.exists_index(target_index)
                alias_exists = await storage.driver.raw.exists_alias(index=target_index, alias=alias_index)

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

                    if 'acknowledged' not in result or result['acknowledged'] is not True:
                        # Index not created

                        logger.error("New {} `{}` was NOT CREATED. The following result was returned {}".format(
                            'template' if index.multi_index else 'index',
                            target_index,
                            result)
                        )
                        continue

                    logger.info("New {} `{}` created. Mapping from `{}` was used.".format(
                        'template' if index.multi_index else 'index',
                        target_index,
                        map_file)
                    )

                    if key in index_mapping and 'on-start' in index_mapping[key]:
                        if index_mapping[key]['on-start'] is not None:
                            logger.info(f"Running on start for index `{key}`.")
                            on_start = index_mapping[key]['on-start']
                            if callable(on_start):
                                await on_start()

                    yield "index", target_index, alias_index

                # elif original_index_exists and not alias_exist:  # Index exists but is not an alias.
                #
                #     # Correct missing alias
                #
                #     target_index_exists = await storage.driver.raw.exists_index(target_index)
                #     if not target_index_exists:
                #         await storage.driver.raw.clone(alias_index, target_index)
                #         await storage.driver.raw.create_alias(target_index, target_index)
                #         logger.info(f'New alias {target_index} for index {alias_index}')
                #     else:
                #         logger.error(f'Target index {target_index} exists. Could not override.')

                else:
                    logger.info("Index `{}` exists.".format(target_index))
