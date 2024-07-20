import json
from elasticsearch import NotFoundError

from tracardi.context import get_context
from tracardi.service.storage.elastic.driver.elastic_client import ElasticClient
from tracardi.service.storage.index import Resource, Index
from tracardi.service.utils.diff import get_changed_values


async def get_indices_status():
    es = ElasticClient.instance()
    for key, index in Resource().resources.items():  # type: str, Index

        if index.multi_index:

            # Template
            _template = index.get_prefixed_template_name()
            if not await es.exists_index_template(_template):
                yield "missing_template", _template
            else:
                yield "existing_template", _template

            # Alias

            _alias = index.get_index_alias()
            _template_pattern = index.get_templated_index_pattern()

            if get_context().is_production():
                has_alias = await es.exists_alias(_alias)
            else:
                has_alias = await es.exists_alias(_alias, index=_template_pattern)

            if not has_alias:
                yield "missing_alias", _alias
            else:
                yield "existing_alias", _alias

        else:

            # Index
            _index = index.get_write_index()
            if not await es.exists_index(_index):
                yield "missing_index", _index
            else:
                yield "existing_index", _index

            # Alias
            _alias = index.get_index_alias()

            if get_context().is_production():
                has_alias = await es.exists_alias(_alias)
            else:
                has_alias = await es.exists_alias(_alias, index=_index)

            if not has_alias:
                yield "missing_alias", _alias
            else:
                yield "existing_alias", _alias


async def check_indices_mappings_consistency():
    """

    This code is checking the mapping of an Elasticsearch
    index against a system mapping file. It loops through
    a dictionary of resources and for each resource, it
    retrieves the system mapping file and loads it into memory.
    It then compares this system mapping to the mapping of an
    Elasticsearch index that is being written to. If there are
    any differences between the two mappings, it saves these
    differences in a dictionary. And, it returns the result dictionary at the end.

    :return: dict
    """

    result = {}

    es = ElasticClient.instance()
    for key, index in Resource().resources.items():  # type: str, Index

        system_mapping_file = index.get_mapping()

        with open(system_mapping_file) as file:
            system_mapping = file.read()
            system_mapping = index.prepare_mappings(system_mapping, index)
            if index.multi_index:
                system_mapping = system_mapping['template']
            del system_mapping['settings']

        try:
            es_mapping = await es.get_mapping(index.get_write_index())
            es_mapping = es_mapping[index.get_write_index()]

            diff = get_changed_values(old_dict=es_mapping, new_dict=system_mapping)
            if diff:
                result[index.get_write_index()] = json.loads(json.dumps(diff, default=str))
        except NotFoundError as e:
            result[index.get_write_index()] = {"Message": str(e)}

    return result
