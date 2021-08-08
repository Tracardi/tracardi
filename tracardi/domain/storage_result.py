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

# x = {
#     "took": 0,
#     "timed_out": False,
#     "_shards": {
#         "total": 1,
#         "successful": 1,
#         "skipped": 0,
#         "failed": 0
#     },
#     "hits": {
#         "total": {
#             "value": 1,
#             "relation": "eq"
#         },
#         "max_score": 0.2876821,
#         "hits": [
#             {
#                 "_index": "test1-tracardi-rule",
#                 "_type": "_doc",
#                 "_id": "my-rule",
#                 "_score": 0.2876821,
#                 "_source": {
#                     "id": "my-rule",
#                     "source": {
#                         "id": "mobile-app"
#                     },
#                     "trigger": "event.type==\"xxx1\"",
#                     "actions": [
#                         {
#                             "module": "tracardi.process_engine.actions.copy_all_action",
#                             "className": "CopyAllAction",
#                             "config": {
#                                 "runOnce": True
#                             }
#                         }
#                     ],
#                     "is_cyclic": False
#                 }
#             }
#         ]
#     }
# }
#
# a = StorageResult(x)
# for q in a:
#     print(q)
