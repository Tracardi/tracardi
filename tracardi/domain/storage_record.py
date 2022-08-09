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

    @staticmethod
    def build_from_base_model(model: BaseModel) -> 'StorageRecord':
        return StorageRecord(**model.dict())

    def __init__(self, *args, **kwargs):
        super(StorageRecord, self).__init__(*args, **kwargs)
        self._meta = None

    def set_metadata(self, meta: RecordMetadata) -> 'StorageRecord':
        self._meta = meta
        return self

    def get_metadata(self) -> RecordMetadata:
        return self._meta

    def has_metadata(self) -> bool:
        return self._meta is not None


class StorageRecords(dict):

    @staticmethod
    def build_from_elastic(elastic_records: dict = None) -> 'StorageRecords':
        if elastic_records is None:
            return StorageRecords()

        if isinstance(elastic_records, StorageRecords):
            return elastic_records

        record = StorageRecords(**elastic_records)
        record.set_data(
            total=elastic_records['hits']['total']['value'],
            records=elastic_records['hits']['hits']
        )
        return record

    def __init__(self, *args, **kwargs):
        super(StorageRecords, self).__init__(*args, **kwargs)
        self.total = 0
        self._hits = []
        self.chunk = 0

    def set_data(self, records, total):
        self.total = total
        self._hits = records
        self.chunk = len(self._hits)

    def __repr__(self):
        return "hits {}, total: {}".format(self._hits, self.total)

    def __iter__(self) -> Iterator[StorageRecord]:
        for hit in self._hits:
            row = StorageRecord.build_from_elastic(hit)
            row['id'] = hit['_id']

            yield row

    def first(self):
        first_hit = self._hits[0]
        row = StorageRecord.build_from_elastic(first_hit)
        row['id'] = first_hit['_id']

        return row

    def dict(self):
        return {
            "total": self.total,
            "result": list(self)
        }

    def transform_hits(self, func: Callable) -> None:
        self._hits = [{**hit, "_source": func(hit["_source"])} for hit in self._hits]

    def __len__(self):
        return self.chunk
