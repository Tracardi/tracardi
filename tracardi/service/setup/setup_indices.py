import json
import os

from tracardi.config import tracardi, elastic
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.setup.setup_plugins import add_plugins
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

    def add_prefix(map):
        map_index_patterns = [
            pattern.replace("%%PREFIX%%-", f"{elastic.instance_prefix}-" if elastic.instance_prefix else "") for pattern
            in map["index_patterns"]]
        map["index_patterns"] = map_index_patterns
        return map

    es = ElasticClient.instance()
    for key, index in resources.resources.items():  # type: str, Index

        if index.mapping:
            map_file = index.mapping
        else:
            map_file = 'mappings/default-dynamic-index.json'

        with open(os.path.join(__local_dir, map_file)) as file:
            map = json.load(file)

            if index.multi_index is True:

                # Replace prefix
                map = add_prefix(map)

                # Multi indices need templates. Index will be create automatically on first insert
                result = await es.put_index_template(index.index, map)

                if 'acknowledged' in result and result['acknowledged'] is True:
                    logger.info(
                        "The template for `{}` index created. Mapping from `{}` was used. The index will be "
                        "auto created from template.".format(
                            index.get_write_index(),
                            map_file)
                    )
                    yield "template", index.get_write_index()

            elif not await es.exists_index(index.get_write_index()):

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
                result = await es.create_index(index.get_write_index(), map)

                if 'acknowledged' not in result or result['acknowledged'] is not True:
                    logger.error("New {} `{}` was not created. The following result was returned {}".format(
                        'template' if index.multi_index else 'index',
                        index.get_write_index(),
                        result)
                    )
                else:
                    logger.info("New {} `{}` created. Mapping from `{}` was used.".format(
                        'template' if index.multi_index else 'index',
                        index.get_write_index(),
                        map_file)
                    )
                    yield "index", index.get_write_index()

                if key in index_mapping and 'on-start' in index_mapping[key]:
                    if index_mapping[key]['on-start'] is not None:
                        on_start = index_mapping[key]['on-start']
                        if callable(on_start):
                            await on_start()
            else:
                logger.info("Index `{}` exists.".format(index.get_write_index()))
