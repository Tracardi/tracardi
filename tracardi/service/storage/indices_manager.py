import json

from deepdiff import DeepDiff

from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.index import resources, Index


async def get_indices_status():
    es = ElasticClient.instance()
    for key, index in resources.resources.items():  # type: str, Index

        if not index.aliased:
            _index = index.get_index_alias()
            if not await es.exists_index(_index):
                yield "missing_index", _index
            else:
                yield "existing_index", _index

        elif not index.multi_index:
            _index = index.get_aliased_data_index()
            if not await es.exists_index(_index):
                yield "missing_index", _index
            else:
                yield "existing_index", _index

            _alias = index.get_index_alias()
            if not await es.exists_alias(_alias, index=_index):
                yield "missing_alias", _alias
            else:
                yield "existing_alias", _alias

        else:
            _template = index.get_prefixed_template_name()
            if not await es.exists_index_template(_template):
                yield "missing_template", _template

            _alias = index.get_index_alias()
            _template_pattern = index.get_template_pattern()
            if not await es.exists_alias(_alias, index=_template_pattern):
                yield "missing_alias", _alias


async def check_indices_mappings_consistency():
    result = {}

    es = ElasticClient.instance()
    for key, index in resources.resources.items():  # type: str, Index
        system_mapping_file = index.get_mapping()

        with open(system_mapping_file) as file:
            system_mapping = file.read()
            system_mapping = index.prepare_mappings(system_mapping)
            system_mapping = json.loads(system_mapping)
            if index.multi_index:
                system_mapping = system_mapping['template']
            del system_mapping['settings']
        es_mapping = await es.get_mapping(index.get_write_index())
        es_mapping = es_mapping[index.get_version_write_index()]

        diff = DeepDiff(es_mapping, system_mapping, exclude_paths=["root['aliases']"])

        if diff:
            result[index.get_version_write_index()] = json.loads(json.dumps(diff.to_dict(), default=str))

        return result
