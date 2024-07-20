import json

from tracardi.domain.resources.elastic_resource_config import ElasticResourceConfig, ElasticCredentials
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.storage.elastic.driver.elastic_client import ElasticClient
from .model.config import Config
from elasticsearch import ElasticsearchException
from tracardi.service.domain import resource as resource_db
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint


def validate(config: dict):
    config = Config(**config)

    # Try parsing JSON just for validation purposes
    try:
        json.loads(config.query)
    except json.JSONDecodeError as e:
        raise ValueError(str(e))

    return config


class Endpoint(PluginEndpoint):

    @staticmethod
    async def fetch_indices(config: dict):
        config = ElasticResourceConfig(**config)
        return await config.get_indices()


class ElasticSearchFetcher(ActionRunner):

    _client: ElasticClient
    config: Config

    async def set_up(self, init):
        config = Config(**init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        credentials = resource.credentials.get_credentials(self, ElasticCredentials)
        self._client = credentials.get_client()

    async def run(self, payload: dict, in_edge=None) -> Result:

        try:
            query = json.loads(self.config.query)

            if 'size' not in query:
                query["size"] = 20

            if query["size"] > 50:
                self.console.warning("Fetching more then 50 records may impact the GUI performance.")

            result = await self._client.search(
                index=self.config.index.id,
                query=query
            )

            await self._client.close()

        except ElasticsearchException as e:
            self.console.error(str(e))
            return Result(port="error", value={
                "message": str(e)
            })

        return Result(port="result", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=ElasticSearchFetcher.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.6.0.1',
            license="MIT + CC",
            author="Dawid Kruk",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "index": None,
                "query": "{\"query\":{\"match_all\":{}}}"
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
                                component=FormComponent(type="resource", props={"label": "Resource",
                                                                                "tag": "elasticsearch"})
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
            group=["Databases"],
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
