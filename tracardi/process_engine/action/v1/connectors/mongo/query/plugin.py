import json
from json import JSONDecodeError

from tracardi.domain.resource import ResourceCredentials
from tracardi.domain.resource_config import ResourceConfig
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.client import MongoClient
from .model.configuration import PluginConfiguration, MongoConfiguration, DatabaseConfig


def validate(config: dict) -> PluginConfiguration:
    config = PluginConfiguration(**config)
    try:
        json.loads(config.query)
    except JSONDecodeError as e:
        raise ValueError("Can not parse this data as JSON. Error: `{}`".format(str(e)))
    return config


class MongoConnectorAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'MongoConnectorAction':
        config = PluginConfiguration(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return MongoConnectorAction(config, resource.credentials)

    def __init__(self, config: PluginConfiguration, credentials: ResourceCredentials):
        mongo_config = credentials.get_credentials(self, output=MongoConfiguration)  # type: MongoConfiguration
        self.client = MongoClient(mongo_config)
        self.config = config

    async def run(self, payload):
        try:
            query = json.loads(self.config.query)
        except JSONDecodeError as e:
            raise ValueError("Can not parse this data as JSON. Error: `{}`".format(str(e)))

        result = await self.client.find(self.config.database.id, self.config.collection.id, query)
        return Result(port="payload", value={"result": result})

    # async def close(self):
    #     await self.client.close()


class Endpoint(PluginEndpoint):

    @staticmethod
    async def fetch_databases(config):
        config = ResourceConfig(**config)
        resource = await storage.driver.resource.load(config.source.id)
        mongo_config = MongoConfiguration(**resource.credentials.production)
        client = MongoClient(mongo_config)
        databases = await client.dbs()
        return {
            "total": len(databases),
            "result": [{"name": db, "id": db} for db in databases]
        }

    @staticmethod
    async def fetch_collections(config):
        config = DatabaseConfig(**config)
        resource = await storage.driver.resource.load(config.source.id)
        mongo_config = MongoConfiguration(**resource.credentials.production)
        client = MongoClient(mongo_config)
        collections = await client.collections(config.database.id)
        return {
            "total": len(collections),
            "result": [{"name": item, "id": item} for item in collections]
        }


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MongoConnectorAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.2',
            license="MIT",
            author="Risto Kowaczewski",
            manual="mongo_query_action",
            init={
                "source": {
                    "id": None,
                },
                "database": None,
                "collection": None,
                "query": "{}"
            },
            form=Form(groups=[
                FormGroup(
                    name="MongoDB connection settings",
                    fields=[
                        FormField(
                            id="source",
                            name="MongoDB resource",
                            description="Select MongoDB resource. Authentication credentials will be used to "
                                        "connect to MongoDB server.",
                            component=FormComponent(
                                type="resource",
                                props={"label": "resource", "tag": "mongo"})
                        )
                    ]
                ),
                FormGroup(
                    name="Query settings",
                    fields=[
                        FormField(
                            id="database",
                            name="Database",
                            description="Select database URI you want to connect to. If you see error select resource "
                                        "first so we know which resource to connect to fetch a list of databases.",
                            component=FormComponent(type="autocomplete", props={
                                "label": "Database URI",
                                "endpoint": {
                                    "url": Endpoint.url(__name__, "fetch_databases"),
                                    "method": "post"
                                }
                            })
                        ),
                        FormField(
                            id="collection",
                            name="Collection",
                            description="Select collection you would like to fetch data from. If you see error select "
                                        "resource and database first so we know which resource and database to connect "
                                        "to fetch a list of collections.",
                            component=FormComponent(type="autocomplete", props={
                                "label": "Collection",
                                "endpoint": {
                                    "url": Endpoint.url(__name__, "fetch_collections"),
                                    "method": "post"
                                }
                            })
                        ),
                        FormField(
                            id="query",
                            name="Query",
                            description="Type query.",
                            component=FormComponent(type="json", props={"label": "Query"})
                        ),
                    ])
            ]),

        ),
        metadata=MetaData(
            name='Mongo connector',
            desc='Connects to mongodb and reads data.',
            icon='mongo',
            group=["Connectors"]
        )
    )
