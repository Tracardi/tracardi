from uuid import uuid4
from elasticsearch import helpers, ElasticsearchException, AsyncElasticsearch
from elasticsearch._async.client.sql import SqlClient
from elasticsearch._async.client.utils import SKIP_IN_PATH, query_params
from elasticsearch.exceptions import NotFoundError, ConnectionError
from fastapi import HTTPException

from ssl import create_default_context

from tracardi import config
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

_singleton = None


class AwsCompatibleSqlClient(SqlClient):

    @query_params()
    async def clear_cursor(self, body, params=None, headers=None):
        """
        Clears the SQL cursor

        `<https://www.elastic.co/guide/en/elasticsearch/reference/7.12/sql-pagination.html>`_

        :arg body: Specify the cursor value in the `cursor` element to
            clean the cursor.
        """
        if body in SKIP_IN_PATH:
            raise ValueError("Empty value passed for a required argument 'body'.")

        return await self.transport.perform_request(
            "POST", "/_sql/close", params=params, headers=headers, body=body
        )

    @query_params("format")
    async def query(self, body, params=None, headers=None):
        """
        Executes a SQL request

        `<https://www.elastic.co/guide/en/elasticsearch/reference/7.12/sql-rest-overview.html>`_

        :arg body: Use the `query` element to start a query. Use the
            `cursor` element to continue a query.
        :arg format: a short version of the Accept header, e.g. json,
            yaml
        """
        if body in SKIP_IN_PATH:
            raise ValueError("Empty value passed for a required argument 'body'.")

        return await self.transport.perform_request(
            "POST", "/_sql", params=params, headers=headers, body=body
        )

    @query_params()
    async def translate(self, body, params=None, headers=None):

        if body in SKIP_IN_PATH:
            raise ValueError("Empty value passed for a required argument 'body'.")

        return await self.transport.perform_request(
            config.elastic.sql_translate_method, config.elastic.sql_translate_url, params=params, headers=headers,
            body=body
        )


class Elastic:

    def __init__(self, **kwargs):
        self._cache = {}
        self._client = AsyncElasticsearch(**kwargs)
        self._client.sql = AwsCompatibleSqlClient(self._client)

    async def translate(self, sql):
        return await self._client.sql.translate(body=sql)

    async def close(self):
        await self._client.close()

    async def get(self, index, id):
        return await self._client.get(index=index, doc_type='_doc', id=id)

    # todo error handling move to service
    async def delete(self, index, id):
        try:
            return await self._client.delete(index=index, doc_type="_doc", id=id)
        except NotFoundError:
            return None

    async def delete_by_query(self, index, body):
        try:
            return await self._client.delete_by_query(index=index, body=body)
        except NotFoundError:
            return None

    # todo error handling move to service
    async def exists(self, index, id):
        try:
            return await self._client.exists(index=index, doc_type="_doc", id=id)
        except NotFoundError:
            return None

    async def search(self, index, query):
        return await self._client.search(index=index, body=query)

    async def scan(self, index, query):

        _generator = helpers.async_scan(
            self._client,
            query=query,
            index=index,
        )

        async for doc in _generator:
            yield doc

    async def insert(self, index, records) -> BulkInsertResult:

        if not isinstance(records, list):
            raise ValueError("Insert expects payload to be list.")

        bulk = []
        ids = []
        for record in records:

            if '_id' in record:
                _id = record['_id']
                del (record['_id'])
            else:
                _id = str(uuid4())

            ids.append(_id)
            record = {
                "_index": index,
                "_id": _id,
                "_source": record
            }

            bulk.append(record)

        success, errors = await helpers.async_bulk(self._client, bulk)

        return BulkInsertResult(
            saved=success,
            errors=errors,
            ids=ids
        )

    async def update(self, index, id, record):
        return await self._client.update(index, body=record, id=id)

    async def remove_index(self, index):
        return await self._client.indices.delete(index=index)

    async def create_index(self, index, mappings):
        return await self._client.indices.create(index=index, ignore=400, body=mappings)

    async def exists_index(self, index):
        return await self._client.indices.exists(index=index)

    async def list_indices(self):
        return await self._client.indices.get("*")

    async def refresh(self, index, params=None, headers=None):
        return await self._client.indices.refresh(index=index, params=params, headers=headers)

    async def flush(self, index, params=None, headers=None):
        return await self._client.indices.flush(index=index, params=params, headers=headers)


    @staticmethod
    def _get_elastic_config():

        kwargs = {}

        if config.elastic.host:
            kwargs['hosts'] = config.elastic.host
        if config.elastic.scheme:
            kwargs['scheme'] = config.elastic.scheme
        if config.elastic.sniffer_timeout:
            kwargs['sniffer_timeout'] = config.elastic.sniffer_timeout
        if config.elastic.sniff_on_start:
            kwargs['sniff_on_start'] = config.elastic.sniff_on_start
        if config.elastic.sniff_on_connection_fail:
            kwargs['sniff_on_connection_fail'] = config.elastic.sniff_on_connection_fail
        if config.elastic.maxsize:
            kwargs['maxsize'] = config.elastic.maxsize

        if config.elastic.cafile:
            context = create_default_context(cafile=config.elastic.cafile)
            kwargs['ssl_context'] = context

        if config.elastic.http_auth_password and config.elastic.http_auth_username:
            kwargs['http_auth'] = (config.elastic.http_auth_username, config.elastic.http_auth_password)

        if config.elastic.cloud_id:
            kwargs['cloud_id'] = config.elastic.cloud_id

        if config.elastic.api_key:
            kwargs['api_key'] = config.elastic.api_key

        if config.elastic.http_compress:
            kwargs['http_compress'] = config.elastic.http_compress

        return kwargs

    @staticmethod
    def instance():

        global _singleton

        def get_elastic_client():
            kwargs = Elastic._get_elastic_config()
            return Elastic(**kwargs)

        if _singleton is None:
            try:
                _singleton = get_elastic_client()
            except (ElasticsearchException, ConnectionError) as e:
                raise HTTPException(status_code=500, detail=str(e))

        return _singleton
