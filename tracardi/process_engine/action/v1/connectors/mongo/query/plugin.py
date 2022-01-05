import json
from json import JSONDecodeError

from tracardi.domain.resource import ResourceCredentials
from tracardi.service.storage.driver import storage
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from .model.client import MongoClient
from .model.configuration import PluginConfiguration, MongoConfiguration


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

        result = await self.client.find(self.config.database, self.config.collection, query)
        return Result(port="payload", value={"result": result})

    # async def close(self):
    #     await self.client.close()


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MongoConnectorAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.1',
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
                            description="Type database URI you want to connect to.",
                            component=FormComponent(type="text", props={"label": "Database URI"})
                        ),
                        FormField(
                            id="collection",
                            name="Collection",
                            description="Type collection you would like to fetch data from.",
                            component=FormComponent(type="text", props={"label": "Collection"})
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

