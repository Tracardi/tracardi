from typing import Optional

from pydantic import BaseModel, validator

from tracardi.config import ElasticConfig
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.driver import storage
from tracardi.service.storage.elastic_client import ElasticClient


class ElasticCredentials(BaseModel):
    url: str
    port: int  # todo remove port not used
    scheme: str
    username: Optional[str] = None
    password: Optional[str] = None
    verify_certs: bool

    def has_credentials(self):
        return self.username is not None and self.password is not None

    def get_client(self) -> ElasticClient:
        return ElasticClient(**ElasticClient.get_elastic_config(ElasticConfig(env={
            "ELASTIC_HOST": self.url,
            "ELASTIC_HTTP_AUTH_USERNAME": self.username,
            "ELASTIC_HTTP_AUTH_PASSWORD": self.password,
            "ELASTIC_SCHEME": self.scheme
        })))


class ElasticResourceConfig(BaseModel):
    source: NamedEntity

    @validator("source")
    def validate_named_entities(cls, value):
        if not value.id:
            raise ValueError(f"This field cannot be empty.")
        return value

    async def get_indices(self):
        """
        It gets indices from production credentials
        """

        resource = await storage.driver.resource.load(self.source.id)
        credentials = ElasticCredentials(**resource.credentials.production)

        client = credentials.get_client()

        indices = await client.list_indices()
        indices = indices.keys()

        return {
            "total": len(indices),
            "result": [{"name": record, "id": record} for record in indices]
        }
