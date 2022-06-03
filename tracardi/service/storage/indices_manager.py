import elasticsearch

from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.index import resources, Index


async def get_indices_status():
    es = ElasticClient.instance()
    for key, index in resources.resources.items():  # type: str, Index

        if not index.aliased:
            _index = index.get_read_index()
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

            _alias = index.get_read_index()
            if not await es.exists_alias(_alias, index=_index):
                yield "missing_alias", _alias
            else:
                yield "existing_alias", _alias

        else:
            _template = index.get_prefixed_template_name()
            if not await es.exists_index_template(_template):
                yield "missing_template", _template

            _alias = index.get_read_index()
            _template_pattern = index.get_template_pattern()
            if not await es.exists_alias(_alias, index=_template_pattern):
                yield "missing_alias", _alias


async def remove_index(index):
    es = ElasticClient.instance()
    index = resources.get_index(index)
    if await es.exists_index(index.get_write_index()):
        try:
            await es.remove_index(index.get_read_index())
        except elasticsearch.exceptions.NotFoundError:
            pass
