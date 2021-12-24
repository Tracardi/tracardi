import logging
from uuid import uuid4
from elasticsearch import helpers, AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from ssl import create_default_context
from tracardi.config import elastic, ON_PREMISES, AWS_CLOUD
from tracardi import config
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

_singleton = None
logger = logging.getLogger(__name__)
logger.setLevel(elastic.logging_level)


class ElasticClient:

    def __init__(self, **kwargs):
        self._cache = {}
        self._client = AsyncElasticsearch(**kwargs)
        # todo remove if not use of sql translate
        # self._client.sql = AwsCompatibleSqlClient(self._client)

    async def close(self):
        await self._client.close()

    async def get(self, index, id):
        logger.debug(f"GET DOCUMENT: {index}, {id}")
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
        logger.debug(f"SEARCH: {index}, {query}")
        return await self._client.search(index=index, body=query)

    async def scan(self, index, query):
        logger.debug(f"SCAN INDEX: {index}, {query}")
        _generator = helpers.async_scan(
            self._client,
            query=query,
            index=index,
        )

        async for doc in _generator:
            yield doc

    async def insert(self, index, records) -> BulkInsertResult:

        logger.debug(f"INSERT: {index}, {records}")

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
        logger.debug(f"REMOVE INDEX: {index}")
        return await self._client.indices.delete(index=index)

    async def create_index(self, index, mappings):
        logger.debug(f"CREATE INDEX: {index}")
        return await self._client.indices.create(index=index, ignore=400, body=mappings)

    async def put_index_template(self, template_name, mappings):
        logger.debug(f"PUT INDEX TEMPLATE: {template_name}")
        return await self._client.indices.put_index_template(name=template_name, ignore=400, body=mappings)

    async def exists_index(self, index):
        logger.debug(f"EXISTS INDEX: {index}")
        return await self._client.indices.exists(index=index)

    async def list_indices(self):
        return await self._client.indices.get("*")

    async def refresh(self, index, params=None, headers=None):
        logger.debug(f"REFRESH INDEX: {index}")
        return await self._client.indices.refresh(index=index, params=params, headers=headers)

    async def flush(self, index, params=None, headers=None):
        logger.debug(f"FLUSH INDEX: {index}")
        return await self._client.indices.flush(index=index, params=params, headers=headers)

    async def update_by_query(self, index, query):
        logger.debug(f"UPDATED BY QUERY on INDEX: {index}")
        return await self._client.update_by_query(index=index, body=query)

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

        if config.elastic.verify_certs is not None:
            kwargs['verify_certs'] = config.elastic.verify_certs

        return kwargs

    @staticmethod
    def instance():

        global _singleton

        def get_elastic_client():
            kwargs = ElasticClient._get_elastic_config()
            if config.elastic.hosting == ON_PREMISES:
                return ElasticClient(**kwargs)
            elif config.elastic.hosting == AWS_CLOUD:
                raise ConnectionError("Not implemented")

        if _singleton is None:
            _singleton = get_elastic_client()

        return _singleton
