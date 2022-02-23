from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .model.config import Config, APIKey
from tracardi.domain.resource import ResourceCredentials
from ..client import AirtableClient, AirtableClientException
from tracardi.service.notation.dict_traverser import DictTraverser


def validate(config: dict) -> Config:
    return Config(**config)


class SendToAirtableAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SendToAirtableAction':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return SendToAirtableAction(
            config=config,
            credentials=resource.credentials
        )

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = AirtableClient(token=credentials.get_credentials(self, APIKey).api_key)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        self.config.mapping = traverser.reshape(self.config.mapping)

        try:
            result = await self.client.add_record(self.config.base_id, self.config.table_name, self.config.mapping)
            return Result(port="response", value=result)

        except AirtableClientException as e:
            return Result(port="error", value={"error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SendToAirtableAction',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            manual="send_to_airtable_action",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "base_id": None,
                "table_name": None,
                "mapping": {}
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Airtable resource",
                                description="Please select your Airtable resource, containing your Airtable API key.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "airtable"})
                            ),
                            FormField(
                                id="base_id",
                                name="Base ID",
                                description="Please provide ID of the base that contains your table. You can find it "
                                            "in the URL when inspecting the base. (https://airtable.com/<BASE-ID>/...)",
                                component=FormComponent(type="text", props={"label": "Base ID"})
                            ),
                            FormField(
                                id="table_name",
                                name="Table name",
                                description="Please provide the exact name of the table that you want to add a record "
                                            "to.",
                                component=FormComponent(type="text", props={"label": "Table"})
                            ),
                            FormField(
                                id="mapping",
                                name="Record mapping",
                                description="Please provide key-value pairs, where key is the name of the record field "
                                            "in your table, and value is path to the value that should be inserted into"
                                            " this field.",
                                component=FormComponent(type="keyValueList", props={"label": "Value"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Send data to Airtable',
            desc='Adds a record to a given table in Airtable, according to provided schema.',
            icon='airtable',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns a response from Airtable if everything is OK."),
                    "error": PortDoc(desc="This port returns some error info if anything goes wrong.")
                }
            )
        )
    )
