from typing import Callable, Iterator

from pydantic import BaseModel


class RecordMetadata(BaseModel):
    id: str
    index: str


class StorageRecord(dict):

    @staticmethod
    def build_from_elastic(elastic_record: dict) -> 'StorageRecord':
        record = StorageRecord(**elastic_record['_source'])
        record.set_metadata(RecordMetadata(id=elastic_record['_id'], index=elastic_record['_index']))
        return record

    def __init__(self, *args, **kwargs):
        super(StorageRecord, self).__init__(*args, **kwargs)
        self._meta = None

    def set_metadata(self, meta: RecordMetadata):
        self._meta = meta

    def get_metadata(self) -> RecordMetadata:
        return self._meta

    def has_metadata(self) -> bool:
        return self._meta is not None


class StorageRecords:
    def __init__(self, result=None):
        if result is None:
            self.total = 0
            self._hits = []
            self.chunk = 0
        else:
            self.total = result['hits']['total']['value']
            self._hits = result['hits']['hits']
            self.chunk = len(self._hits)

    def __repr__(self):
        return "hits {}, total: {}".format(self._hits, self.total)

    def __iter__(self) -> Iterator[StorageRecord]:
        for hit in self._hits:
            row = StorageRecord.build_from_elastic(hit)
            row['id'] = hit['_id']

            yield row

    def dict(self):
        return {
            "total": self.total,
            "result": list(self)
        }

    def transform_hits(self, func: Callable) -> None:
        self._hits = [{**hit, "_source": func(hit["_source"])} for hit in self._hits]

    def __len__(self):
        return self.chunk
