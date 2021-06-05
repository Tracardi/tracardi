from elasticsearch import Elasticsearch, helpers
from elasticsearch.client import SqlClient
from elasticsearch.client.utils import query_params, SKIP_IN_PATH
from elasticsearch.helpers import scan

from app import config


class AwsCompatibleSqlClient(SqlClient):

    @query_params()
    def translate(self, body, params=None, headers=None):

        if body in SKIP_IN_PATH:
            raise ValueError("Empty value passed for a required argument 'body'.")

        return self.transport.perform_request(
            config.elastic.sql_translate_method, config.elastic.sql_translate_url, params=params, headers=headers,
            body=body
        )


class Elastic:

    def __init__(self, **kwargs):
        self._cache = {}
        self._client = Elasticsearch(**kwargs)
        self._client.sql = AwsCompatibleSqlClient(self._client)
        self.sql = self._client.sql

    def get(self, index, id):
        return self._client.get(index=index, doc_type='_doc', id=id)

    def delete(self, index, id):
        return self._client.delete(index=index, doc_type="_doc", id=id)

    def exists(self, index, id):
        return self._client.exists(index=index, doc_type="_doc", id=id)

    def search(self, index, query):
        return self._client.search(index=index, body=query)

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
                del (record['_id'])
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

    def update(self, index, id, record):
        return self._client.update(index, body=record, id=id)

    def remove_index(self, index):
        return self._client.indices.delete(index=index)

    def exists_index(self, index):
        return self._client.indices.exists(index=index)

    def create_index(self, index, mapping):
        return self._client.indices.create(index, body=mapping)
