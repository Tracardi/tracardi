from typing import List, Optional

import elasticsearch

from tracardi.domain.storage_result import StorageResult
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage import index
from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.index import Index


class ElasticFiledSort:
    def __init__(self, field: str, order: str = None, format: str = None):
        self.format = format
        self.order = order
        self.field = field

    def to_query(self):
        if self.field is not None and self.order is None and self.format is None:
            return self.field
        elif self.field is not None and self.order is not None:
            output = {
                self.field: {
                    "order": self.order
                }
            }

            if self.format is not None:
                output[self.field]['format'] = self.format

            return output
        else:
            raise ValueError("Invalid ElasticFiledSort.")


class ElasticStorage:

    def __init__(self, index_key):
        self.storage = ElasticClient.instance()
        if index_key not in index.resources:
            raise ValueError("There is no index defined for `{}`.".format(index_key))
        self.index = index.resources[index_key]  # type: Index
        self.index_key = index_key

    async def exists(self, id) -> bool:
        return await self.storage.exists(self.index.get_index_alias(), id)

    async def count(self, query: dict = None) -> bool:
        return await self.storage.count(self.index.get_index_alias(), query)

    async def load(self, id) -> [dict, None]:

        try:
            index = self.index.get_index_alias()
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
            return await self.storage.delete(self.index.get_index_alias(), id)
        else:
            return await self.delete_by("_id", id)

    async def search(self, query):
        return await self.storage.search(self.index.get_index_alias(), query)

    async def refresh(self, params=None, headers=None):
        return await self.storage.refresh(self.index.get_index_alias(), params, headers)

    async def reindex(self, source, destination, wait_for_completion=True):
        return await self.storage.reindex(source, destination, wait_for_completion=wait_for_completion)

    async def load_by_query_string(self, query_string, limit=100):
        query = {
            "size": limit,
            "query": {
                "query_string": {
                    "query": query_string
                }
            }
        }
        return await self.search(query)

    async def count_by_query_string(self, query_string: str, time_range: str):

        if query_string:
            query = {
                "size": 0,
                "query": {
                    "query_string": {
                        "query": f"metadata.time.insert:[now{time_range} TO now] AND ({query_string})"
                    }
                },
            }
        else:
            query = {
                "size": 0,
                "query": {
                    "query_string": {
                        "query": f"metadata.time.insert:[now{time_range} TO now]"
                    }
                },
            }
        return (await self.search(query))["hits"]["total"]["value"]

    async def load_by(self, field, value, limit=100):
        query = {
            "size": limit,
            "query": {
                "term": {
                    field: value
                }
            }
        }
        return await self.search(query)

    async def match_by(self, field, value, limit=100):
        query = {
            "size": limit,
            "query": {
                "match": {
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
        return await self.storage.delete_by_query(self.index.get_index_alias(), query)

    async def load_by_values(self, fields_and_values: List[tuple], sort_by: Optional[List[ElasticFiledSort]] = None,
                             limit=1000):

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

        if sort_by:
            sort_by_query = []
            for field in sort_by:
                if isinstance(field, ElasticFiledSort):
                    sort_by_query.append(field.to_query())
            if sort_by_query:
                query['sort'] = sort_by_query

        result = await self.search(query)
        return result

    async def flush(self, params, headers):
        return await self.storage.flush(self.index.get_write_index(), params, headers)

    async def update_by_query(self, query):
        return await self.storage.update_by_query(index=self.index.get_index_alias(), query=query)

    async def update(self, id, record, retry_on_conflict=3):
        return await self.storage.update(index=self.index.get_write_index(),
                                         record=record,
                                         id=id,
                                         retry_on_conflict=retry_on_conflict)

    async def delete_by_query(self, query):
        return await self.storage.delete_by_query(index=self.index.get_index_alias(), body=query)

    async def get_mapping(self, index):
        return await self.storage.get_mapping(index)
