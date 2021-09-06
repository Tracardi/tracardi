class StorageResult:
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

    def __iter__(self):
        for hit in self._hits:
            row = hit['_source']
            row['id'] = hit['_id']
            yield row

    def dict(self):
        return {
            "total": self.total,
            "result": list(self)
        }

    def __len__(self):
        return self.chunk
