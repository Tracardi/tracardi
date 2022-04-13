import elasticsearch

from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.index import resources, Index


async def get_missing_indices():
    es = ElasticClient.instance()
    for key, index in resources.resources.items():  # type: str, Index
        _index = index.get_write_index()
        if not index.multi_index:
            if not await es.exists_index(_index):
                yield "missing", _index
            else:
                yield "exists", _index


async def remove_index(index):
    es = ElasticClient.instance()
    index = resources.resources[index]
    if await es.exists_index(index.get_write_index()):
        try:
            await es.remove_index(index.get_read_index())
        except elasticsearch.exceptions.NotFoundError:
            pass
