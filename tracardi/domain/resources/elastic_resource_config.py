from typing import Optional

from pydantic import field_validator, BaseModel

from tracardi.config import ElasticConfig
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.domain import resource as resource_db
from tracardi.service.storage.elastic.driver.elastic_client import ElasticClient


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

    @field_validator("source")
    @classmethod
    def validate_named_entities(cls, value):
        if not value.id:
            raise ValueError("This field cannot be empty.")
        return value

    async def get_indices(self):
        """
        It gets indices from production credentials
        """

        resource = await resource_db.load(self.source.id)
        credentials = ElasticCredentials(**resource.credentials.production)

        client = credentials.get_client()

        indices = await client.list_indices()
        aliases = await client.list_aliases()
        indices = [("I", item) for item in indices.keys()]

        list_of_aliases = []
        for alias in aliases.values():
            if 'aliases' in alias:
                for _alias in alias['aliases']:
                    list_of_aliases.append(("A", _alias))

        aliases_and_indices = list_of_aliases + indices

        return {
            "total": len(aliases_and_indices),
            "result": [{"name": f"({record[0]}) {record[1]}", "id": record[1]} for record in aliases_and_indices]
        }
