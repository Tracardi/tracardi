from typing import Iterator, List, Union, Tuple, Optional, TypeVar, Type, Dict
from pydantic import BaseModel


T = TypeVar('T')


class RecordMetadata(BaseModel):
    id: str
    index: str


class StorageRecord(dict):

    @staticmethod
    def _get_inner_hits(elastic_record):
        if 'inner_hits' in elastic_record:
            for name, inner_hits in elastic_record['inner_hits'].items():
                yield name, StorageRecords.build_from_elastic(inner_hits)

    @staticmethod
    def build_from_elastic(elastic_record: dict) -> 'StorageRecord':
        if '_source' not in elastic_record:
            raise ValueError("No data in StorageRecord. Source does not exist.")
        record = StorageRecord(**elastic_record['_source'])
        record.set_meta_data(RecordMetadata(id=elastic_record['_id'], index=elastic_record['_index']))
        if 'inner_hits' in elastic_record:
            for name, inner_hits in StorageRecord._get_inner_hits(elastic_record):
                record.set_inner_hits(name, inner_hits)
        return record

    @staticmethod
    def build_from_base_model(model: BaseModel, exclude=None) -> 'StorageRecord':
        return StorageRecord(**model.model_dump(exclude=exclude))

    @staticmethod
    def build_from_dict(data: dict) -> 'StorageRecord':
        return StorageRecord(**data)

    def __init__(self, *args, **kwargs):
        super(StorageRecord, self).__init__(*args, **kwargs)
        self._meta = None
        self._inner_hits = {}

    def set_inner_hits(self, name, data):
        self._inner_hits[name] = data

    def get_inner_hit(self, name) -> Dict[str, 'StorageRecords']:
        return self._inner_hits[name]

    def get_inner_hits(self) -> Dict[str, 'StorageRecords']:
        return self._inner_hits

    def has_inner_hits(self) -> bool:
        return bool(self._inner_hits)

    def set_meta_data(self, meta: RecordMetadata) -> 'StorageRecord':
        self._meta = meta
        return self

    def get_meta_data(self) -> Optional[RecordMetadata]:
        return self._meta

    def has_meta_data(self) -> bool:
        return self._meta is not None

    def to_entity(self, model: Type[T]) -> T:
        _object = model(**self)
        return _object.set_meta_data(self.get_meta_data())

    def serialize(self):
        return {
            "profile": self,
            "storage": self.get_meta_data().model_dump()
        }


class StorageAggregate(dict):

    def __init__(self, *args, **kwargs):
        super(StorageAggregate, self).__init__(*args, **kwargs)
        if 'buckets' in kwargs:
            self._buckets = kwargs['buckets']

    def buckets(self):
        return self._buckets


class StorageAggregates(dict):

    def __iter__(self) -> Iterator[Tuple[str, StorageAggregate]]:
        for bucket_name, value in self.items():
            yield bucket_name, StorageAggregate(**value)

    def convert(self, aggregate_key) -> Iterator[Tuple[str, dict]]:
        for bucket, data in self:
            records = {}
            if "buckets" in data:
                for item in data['buckets']:
                    records[item[aggregate_key]] = item['doc_count']
            else:
                records = {"found": data["doc_count"]}

            if 'sum_other_doc_count' in data:
                records['other'] = data['sum_other_doc_count']
            yield bucket, records


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
            records=elastic_records['hits']['hits'],
            aggregations=elastic_records['aggregations'] if 'aggregations' in elastic_records else None
        )
        return record

    def __init__(self, *args, **kwargs):
        super(StorageRecords, self).__init__(*args, **kwargs)
        self.total = 0
        self._hits = []  # type: List[dict]
        self.chunk = 0
        self._aggregations = None
        # self._meta = None

    def set_data(self, records, total, aggregations: dict = None):
        self.total = total
        self._hits = records
        self.chunk = len(self._hits)
        self._aggregations = aggregations

    def aggregations(self, key=None) -> Union[StorageAggregate, StorageAggregates]:
        if key is None:
            return StorageAggregates(self._aggregations) if self._aggregations is not None else None
        if self._aggregations is None or key not in self._aggregations:
            raise ValueError(f"Aggregation `{key}` not available. No aggregation set for this query")
        return StorageAggregate(**self._aggregations[key])

    @staticmethod
    def _to_record(hit) -> 'StorageRecord':
        row = StorageRecord.build_from_elastic(hit)
        row['id'] = hit['_id']

        return row

    def __repr__(self):
        return "hits {}, total: {}, aggregations: {}".format(self._hits, self.total, self._aggregations)

    def __iter__(self) -> Iterator[StorageRecord]:
        for hit in self._hits:
            yield self._to_record(hit)

    def __getitem__(self, subscript) -> Union[List[StorageRecord], StorageRecord]:
        if isinstance(subscript, slice):
            return [self._to_record(row) for row in self._hits[subscript.start:subscript.stop:subscript.step]]
        else:
            hit = self._hits[subscript]
            return self._to_record(hit)

    def row(self, n):
        """
        Return row data the same way as elastic does.
        """
        try:
            return self._hits[n]
        except Exception:
            return None

    def first(self) -> Optional[StorageRecord]:
        if len(self._hits) > 0:
            first_hit = self._hits[0]
            row = StorageRecord.build_from_elastic(first_hit)
            row['id'] = first_hit['_id']

            return row
        return None

    def dict(self):
        hits = []
        for hit in self:
            _hit = hit
            if hit.has_inner_hits():
                _hit['_inner_hits'] = {name: data.dict() for name, data in hit.get_inner_hits().items()}
            hits.append(_hit)

        return {
            "total": self.total,
            "result": hits
        }

    # def transform_hits(self, func: Callable) -> None:
    #     self._hits = [{**hit, "_source": func(hit["_source"])} for hit in self._hits]

    @staticmethod
    def _make_domain_object(domain_object: Type[T], record: StorageRecord) -> T:
        domain = domain_object(**record)
        meta = record.get_meta_data()
        if meta:
            domain.set_meta_data(meta)
        return domain

    def to_domain_objects(self, domain_object: Type[T]) -> List[T]:
        return [self._make_domain_object(domain_object, hit) for hit in self]

    def __len__(self):
        return self.chunk

    def __bool__(self):
        return len(self._hits) != 0

