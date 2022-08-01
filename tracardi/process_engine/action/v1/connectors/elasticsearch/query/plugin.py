import json

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config, ElasticCredentials
from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials
from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint


def validate(config: dict):
    config = Config(**config)

    # Try parsing JSON just for validation purposes
    try:
        json.loads(config.query)
    except json.JSONDecodeError as e:
        raise ValueError(str(e))

    return config


class ElasticSourceConfig(BaseModel):
    source: NamedEntity

    @validator("source")
    def validate_named_entities(cls, value):
        if not value.id:
            raise ValueError(f"This field cannot be empty.")
        return value


class Endpoint(PluginEndpoint):

    @staticmethod
    async def fetch_indices(config: dict):
        config = ElasticSourceConfig(**config)
        resource = await storage.driver.resource.load(config.source.id)
        credentials = ElasticCredentials(**resource.credentials.production)

        if credentials.has_credentials():
            client = ElasticClient(
                hosts=credentials.get_url(),
                http_auth=(credentials.username, credentials.password),
                scheme=credentials.scheme,
                port=credentials.port
            )
        else:
            client = ElasticClient(
                hosts=credentials.get_url(),
                scheme=credentials.scheme,
                port=credentials.port
            )

        indices = await client.list_indices()
        indices = indices.keys()

        return {
            "total": len(indices),
            "result": [{"name": record, "id": record} for record in indices]
        }


class ElasticSearchFetcher(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'ElasticSearchFetcher':
        config = Config(**kwargs)
        credentials = await storage.driver.resource.load(config.source.id)
        return ElasticSearchFetcher(config, credentials.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        credentials = credentials.get_credentials(self, ElasticCredentials)

        if credentials.has_credentials():
            self._client = ElasticClient(
                hosts=credentials.get_url(),
                http_auth=(credentials.username, credentials.password),
                scheme=credentials.scheme,
                port=credentials.port
            )
        else:
            self._client = ElasticClient(
                hosts=credentials.get_url(),
                scheme=credentials.scheme,
                port=credentials.port
            )

    async def run(self, payload: dict, in_edge=None) -> Result:

        try:
            res = await self._client.search(
                index=self.config.index.id,
                query=json.loads(self.config.query)
            )
            await self._client.close()

        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={})

        return Result(port="result", value=res)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ElasticSearchFetcher',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "index": None,
                "query": "{\"query\":{}}"
            },
            manual="elasticsearch_query_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Elasticsearch resource",
                                description="Please select your Elasticsearch resource.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "elastic"})
                            ),
                            FormField(
                                id="index",
                                name="Elasticsearch index",
                                description="Please select Elasticsearch index you want to search.",
                                component=FormComponent(type="autocomplete", props={
                                    "label": "Index",
                                    "endpoint": {
                                        "url": Endpoint.url(__name__, "fetch_indices"),
                                        "method": "post"
                                    }
                                })
                            ),
                            FormField(
                                id="query",
                                name="Query",
                                description="Please provide Elasticsearch DSL query.",
                                component=FormComponent(type="json", props={"label": "DSL query"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Query Elasticsearch',
            desc='Gets data from given Elasticsearch resource',
            icon='elasticsearch',
            group=["Connectors"],
            tags=['database', 'nosql'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns result of querying ElasticSearch instance."),
                    "error": PortDoc(desc="This port returns error if one occurs, or if received result contains more "
                                          "than 20 records.")
                }
            )
        )
    )
