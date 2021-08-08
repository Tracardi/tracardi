class AggResult:
    def __init__(self, agg_key, result=None, return_counts=True):
        self.return_counts = return_counts
        if result is None:
            self.total = 0
            self._hits = []
        else:
            self.total = result['hits']['total']['value']
            self._hits = result['aggregations'][agg_key]['buckets']

    def __repr__(self):
        return "hits {}, total: {}".format(self._hits, self.total)

    def __iter__(self):
        for hit in self._hits:
            row = hit['key']
            if self.return_counts:
                count = hit['doc_count']
                yield {row: count}
            else:
                yield row

    def dict(self):
        return {
            "total": self.total,
            "result": list(self)
        }
