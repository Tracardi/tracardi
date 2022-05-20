import elasticsearch

from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.index import resources, Index


async def get_indices_status():
    es = ElasticClient.instance()
    for key, index in resources.resources.items():  # type: str, Index

        if not index.multi_index:
            _index = index.get_aliased_data_index()
            if not await es.exists_index(_index):
                yield "missing_index", _index
            else:
                yield "existing_index", _index
        else:
            _template = index.get_prefixed_template_name()
            if not await es.exists_index_template(_template):
                yield "missing_template", _template
            else:
                yield "existing_template", _template


async def remove_index(index):
    es = ElasticClient.instance()
    index = resources.resources[index]
    if await es.exists_index(index.get_write_index()):
        try:
            await es.remove_index(index.get_read_index())
        except elasticsearch.exceptions.NotFoundError:
            pass
