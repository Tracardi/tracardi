from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import scan


class Elastic:

    def __init__(self, host, port=9200):
        self._cache = {}
        self._client = Elasticsearch([{'host': host, 'port': port}])

    def get(self, index, id):
        return self._client.get(index=index, doc_type='_doc', id=id)

    def delete(self, index, id):
        return self._client.delete(index=index, doc_type="_doc", id=id)

    def scan(self, index, query):

        _generator = scan(
            self._client,
            query=query,
            index=index,
        )

        for doc in _generator:
            yield doc

    def insert(self, index, records):
        bulk = []

        for record in records:

            if '_id' in record:
                _id = record['_id']
                del(record['_id'])
                record = {
                    "_index": index,
                    "_id": _id,
                    "_source": record
                }
            else:
                record = {
                    "_index": index,
                    "_source": record
                }

            bulk.append(record)
        return helpers.bulk(self._client, bulk)

    def update(self, index, records):
        bulk = []

        for record in records:
            _id = record['_id']
            del (record['_id'])
            bulk.append({
                "_index": index,
                "_id": _id,
                "_source": {"doc": record},
                "_op_type": "update"
            })

        return helpers.bulk(self._client, bulk)

    def remove_index(self, index):
        return self._client.indices.delete(index=index)