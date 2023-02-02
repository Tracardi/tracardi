from typing import Optional, Union, List
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from ssl import create_default_context
from tracardi.worker.domain.named_entity import NamedEntity


class ElasticCredentials(BaseModel):
    url: Union[str, List[str]]
    port: int
    scheme: str
    username: Optional[str] = None
    password: Optional[str] = None
    verify_certs: bool = True
    cafile: Optional[str] = None
    api_key_id: Optional[str] = None
    api_key: Optional[str] = None
    cloud_id: Optional[str] = None
    maxsize: Optional[str] = None
    http_compress: Optional[str] = None

    def has_credentials(self):
        return self.username is not None and self.password is not None

    def get_hosts(self):
        return self.url.split(",") if isinstance(self.url, str) else self.url


class ElasticImporter(BaseModel):
    index: NamedEntity
    batch: int

    @staticmethod
    def _get_elastic_config(credentials: ElasticCredentials):

        kwargs = {}

        if credentials.url:
            kwargs['hosts'] = credentials.get_hosts()
        if credentials.scheme:
            kwargs['scheme'] = credentials.scheme
        if credentials.maxsize:
            kwargs['maxsize'] = credentials.maxsize

        if credentials.cafile:
            context = create_default_context(cafile=credentials.cafile)
            kwargs['ssl_context'] = context

        if credentials.has_credentials():
            kwargs['http_auth'] = (credentials.username, credentials.password)

        if credentials.cloud_id:
            kwargs['cloud_id'] = credentials.cloud_id

        if credentials.api_key and credentials.api_key_id:
            kwargs['api_key'] = (credentials.api_key_id, credentials.api_key)

        if credentials.http_compress:
            kwargs['http_compress'] = credentials.http_compress

        if credentials.verify_certs is not None:
            kwargs['verify_certs'] = credentials.verify_certs

        return kwargs

    def data(self, credentials: ElasticCredentials):

        client = Elasticsearch(**self._get_elastic_config(credentials))

        result = client.count(body={
            "query": {
                "match_all": {}
            }
        }, index=self.index.id)

        number_of_records = result['count']
        if number_of_records > 0:
            for batch_number, start in enumerate(range(0, number_of_records, self.batch)):
                query = {
                    "query": {
                        "match_all": {}
                    },
                    "from": start,
                    "size": self.batch
                }
                result = client.search(body=query, index=self.index.id)
                for record, data in enumerate(result['hits']['hits']):
                    data = data['_source']
                    progress = ((start + record + 1) / number_of_records) * 100
                    yield data, progress, batch_number + 1

        client.close()
