import json

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from .model.config import Config, Credentials
from elasticsearch import AsyncElasticsearch, ElasticsearchException
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials
from tracardi_plugin_sdk.domain.result import Result


def validate(config: dict):
    config = Config(**config)

    # Try parsing JSON just for validation purposes
    try:
        json.loads(config.query)
    except json.JSONDecodeError as e:
        raise ValueError(str(e))

    return config


class ElasticSearchFetcher(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'ElasticSearchFetcher':
        config = Config(**kwargs)
        credentials = await storage.driver.resource.load(config.source.id)
        return ElasticSearchFetcher(config, credentials.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        credentials = credentials.get_credentials(self, Credentials)

        self._client = AsyncElasticsearch(
            [credentials.url],
            http_auth=(credentials.username, credentials.password),
            scheme=credentials.scheme,
            port=credentials.port
        )

    async def run(self, payload):

        try:
            res = await self._client.search(
                index=self.config.index,
                body=json.loads(self.config.query),
                size=20
            )
            await self._client.close()

        except ElasticsearchException as e:
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
                                component=FormComponent(type="text", props={"label": "index"})
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
