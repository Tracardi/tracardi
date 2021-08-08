from typing import List

import elasticsearch

from tracardi.domain.storage_result import StorageResult
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage import index
from tracardi.service.storage.elastic import Elastic
from tracardi.service.storage.index import Index


class ElasticStorage:

    def __init__(self, index_key):
        self.storage = Elastic.instance()
        self.index = index.resources[index_key]  # type: Index

    async def load(self, id) -> [dict, None]:

        try:
            index = self.index.get_read_index()
            if not self.index.multi_index:
                result = await self.storage.get(index, id)
                output = result['_source']
                output['id'] = result['_id']
            else:
                query = {
                    "query": {
                        "term": {
                            "_id": id
                        }
                    }
                }
                result = StorageResult(await self.storage.search(index, query))
                output = list(result)
                if len(output) != 1:
                    return None
                output = output[0]

            return output
        except elasticsearch.exceptions.NotFoundError:
            return None

    async def create(self, payload) -> BulkInsertResult:
        return await self.storage.insert(self.index.get_write_index(), payload)

    async def delete(self, id):
        if not self.index.multi_index:
            return await self.storage.delete(self.index.get_read_index(), id)
        else:
            return await self.delete_by("_id", id)

    async def search(self, query):
        return await self.storage.search(self.index.get_read_index(), query)

    async def translate(self, sql):
        return await self.storage.translate(sql)

    async def refresh(self, params=None, headers=None):
        return await self.storage.refresh(self.index.get_write_index(), params, headers)

    async def load_by(self, field, value):
        query = {
            "query": {
                "term": {
                    field: value
                }
            }
        }
        return await self.search(query)

    async def delete_by(self, field, value):
        query = {
            "query": {
                "term": {
                    field: value
                }
            }
        }
        return await self.storage.delete_by_query(self.index.get_read_index(), query)

    async def load_by_values(self, fields_and_values: List[tuple], limit=1000):

        terms = []
        for field, value in fields_and_values:
            terms.append({
                "term": {
                    f"{field}": value
                }
            })

        query = {
            "size": limit,
            "query": {
                "bool": {
                    "must": terms
                }
            }
        }

        return await self.search(query)

    async def flush(self, params, headers):
        return await self.storage.flush(self.index.get_write_index(), params, headers)
