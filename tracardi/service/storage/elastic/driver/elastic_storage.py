from collections import defaultdict
from typing import List, Optional, Union, AsyncGenerator, Any, Dict

import elasticsearch
from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.storage_record import StorageRecords, StorageRecord
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.exceptions.exception import DuplicatedRecordException
from tracardi.service.storage.elastic.driver.elastic_client import ElasticClient
from tracardi.service.storage.index import Index, Resource


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
        resource = Resource()
        if index_key not in resource:
            raise ValueError("There is no index defined for `{}`.".format(index_key))
        self.index = resource[index_key]  # type: Index
        self.index_key = index_key

    async def exists(self, id) -> bool:
        if self.index.multi_index:
            return await self.load(id) is not None
        return await self.storage.exists(self.index.get_index_alias(), id)

    async def count(self, query: Optional[dict] = None) -> dict:
        """
        It counts by alias
        """

        index = self.index.get_index_alias()

        return await self.storage.count(index, query)

    async def load(self, id) -> Optional[StorageRecord]:
        try:
            index = self.index.get_index_alias()
            if not self.index.multi_index:
                result = await self.storage.get(index, id)
                output = StorageRecord.build_from_elastic(result)
                output['id'] = result['_id']

            else:
                query = {
                    "query": {
                        "term": {
                            '_id': id
                        }
                    }
                }
                result = await self.storage.search(index, query)
                records = StorageRecords.build_from_elastic(result)

                if len(records) == 0:
                    return None

                if len(records) > 1:
                    raise DuplicatedRecordException(f"Duplicated record {id} in index {index}. Search result: {records}")

                output = records.first()

            return output
        except elasticsearch.exceptions.NotFoundError:
            return None

    @staticmethod
    def _get_storage_record(record, replace_id, exclude=None) -> StorageRecord:
        if isinstance(record, StorageRecord):
            return record

        elif isinstance(record, Entity):
            record = record.to_storage_record(exclude=exclude)

        elif isinstance(record, BaseModel):
            record = StorageRecord.build_from_base_model(record, exclude=exclude)

        else:
            # todo add exclude if possible
            record = StorageRecord(**record)

        if replace_id is True and 'id' in record:
            record['_id'] = record['id']

        return record

    def get_storage_index(self, record) -> str:
        if isinstance(record, Entity) or isinstance(record, StorageRecord):
            if not record.has_meta_data():
                index = self.index.get_write_index()
            else:
                meta = record.get_meta_data()
                if meta.index is None:
                    index = self.index.get_write_index()
                else:
                    index = meta.index
        else:
            index = self.index.get_write_index()
        return index

    async def create(self, data: Union[StorageRecord, Entity, BaseModel, dict, list],
                     replace_id: bool = True, exclude=None) -> Union[BulkInsertResult, List[BulkInsertResult]]:
        if isinstance(data, (list, set)):

            if len(data) == 0:
                return BulkInsertResult()

            records_by_index = defaultdict(list)
            for row in data:
                index = self.get_storage_index(row)
                record = self._get_storage_record(row, exclude=exclude, replace_id=replace_id)
                records_by_index[index].append(record)

            if len(records_by_index) > 1:
                raise ValueError(f"Can not save set of records with mixed target indices. Got the following "
                                 f"indices [{list(records_by_index.keys())}]")

            index, records = list(records_by_index.items())[0]

        else:

            record = self._get_storage_record(data, exclude=exclude, replace_id=replace_id)
            index = self.get_storage_index(record)
            records = [record]
        return await self.storage.insert(index, records)

    async def delete(self, id: str, index: str):
        if index is None:
            raise ValueError("Index can not be None when deleting data.")

        if not self.index.multi_index:  # Single
            # This function does not work on aliases
            return await self.storage.delete(index, id)
        else:
            return await self.delete_by('_id', id, index)

    async def bulk_delete(self, record_ids):
        return await self.storage.delete_bulk(
            index=self.index.get_index_alias(),
            record_ids=record_ids
        )

    async def search(self, query) -> StorageRecords:
        return StorageRecords.build_from_elastic(await self.storage.search(self.index.get_index_alias(), query))

    async def refresh(self, params=None, headers=None):
        return await self.storage.refresh(self.index.get_index_alias(), params, headers)

    async def reindex(self, source, destination, wait_for_completion=True):
        return await self.storage.reindex(source, destination, wait_for_completion=wait_for_completion)

    async def scan(self, query: dict = None, batch: int = 1000) -> AsyncGenerator[StorageRecord, Any]:
        async for row in self.storage.scan(self.index.get_index_alias(), query, size=batch):
            yield StorageRecord.build_from_elastic(row)

    async def load_by_query_string(self, query_string, limit=100) -> StorageRecords:
        query = {
            "size": limit,
            "query": {
                "query_string": {
                    "query": query_string
                }
            }
        }
        return await self.search(query)

    async def count_by_query_string(self, query_string: str, time_range: str) -> StorageRecords:

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

        return await self.search(query)

    async def load_by(self, field, value, limit=100, sort: List[Dict[str, Dict]] = None) -> StorageRecords:
        query = {
            "size": limit,
            "query": {
                "term": {
                    field: value
                }
            }
        }
        if sort:
            query['sort'] = sort
        return await self.search(query)

    async def match_by(self, field, value, limit=100) -> StorageRecords:
        query = {
            "size": limit,
            "query": {
                "match": {
                    field: value
                }
            }
        }
        return await self.search(query)

    async def delete_by(self, field, value, index: str = None):
        query = {
            "query": {
                "term": {
                    field: value
                }
            }
        }

        if index is None:
            index = self.index.get_index_alias()

        return await self.storage.delete_by_query(index, query)

    async def load_by_values(self, fields_and_values: List[tuple],
                             sort_by: Optional[List[ElasticFiledSort]] = None,
                             limit=1000,
                             condition='must'
                             ) -> StorageRecords:

        if condition not in ['must', 'should']:
            raise AssertionError(f"Can not use {condition} for querying elasticsearch.")

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
                    condition: terms
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

    async def update_by_query(self, query, conflicts: str = 'abort', wait_for_completion: bool = None):
        return await self.storage.update_by_query(
            index=self.index.get_index_alias(),
            query=query,
            conflicts=conflicts,
            wait_for_completion=wait_for_completion
        )

    async def update(self, id, record, index, retry_on_conflict=3):
        return await self.storage.update(index=index,
                                         record=record,
                                         id=id,
                                         retry_on_conflict=retry_on_conflict)

    async def delete_by_query(self, query):
        return await self.storage.delete_by_query(index=self.index.get_index_alias(), body=query)

    async def get_mapping(self, index: str):
        return await self.storage.get_mapping(index)

    async def set_mapping(self, index: str, mapping: dict):
        return await self.storage.set_mapping(index, mapping)
