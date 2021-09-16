from collections import defaultdict


class StorageAggregateResult:
    def __init__(self, result=None):
        print(result)
        if result is None:
            self.total = 0
            self.aggregations = []
            self.no_of_aggregates = 0
        else:
            aggrs = defaultdict(list)
            for bucket, data in result['aggregations'].items():
                records = {record['key']: record['doc_count'] for record in data['buckets']}
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
