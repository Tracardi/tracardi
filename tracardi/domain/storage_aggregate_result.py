from collections import defaultdict
from typing import Callable, Tuple, Any


class StorageAggregateResult:
    def __init__(self, result=None, aggregate_key='key'):
        if result is None:
            self.total = 0
            self.aggregations = []
            self.no_of_aggregates = 0
        else:
            aggrs = defaultdict(list)
            for bucket, data in result['aggregations'].items():
                records = {record[aggregate_key]: record['doc_count'] for record in data['buckets']} if \
                    "buckets" in data else {"found": data["doc_count"]}
                if 'sum_other_doc_count' in data:
                    records['other'] = data['sum_other_doc_count']
                aggrs[bucket].append(records)

            self.total = result['hits']['total']['value']
            self.aggregations = aggrs
            self.no_of_aggregates = len(self.aggregations)

    def __repr__(self):
        return "aggregations {}, total: {}".format(self.aggregations, self.total)

    def __len__(self):
        return self.no_of_aggregates

    def process(self, function: Callable, bucket_name=None):
        for bucket, items in self.iterate(bucket_name):
            yield bucket, function(items)

    def iterate(self, bucket_name=None) -> Tuple[str, Any]:
        if bucket_name is not None and bucket_name in self.aggregations:
            for item in self.aggregations[bucket_name]:
                yield bucket_name, item
        else:
            for bucket in self.aggregations:
                for item in bucket:
                    yield bucket, item
