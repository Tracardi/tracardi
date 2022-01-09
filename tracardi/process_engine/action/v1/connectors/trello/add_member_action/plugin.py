from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.action_runner import ActionRunner
from .model.config import Config
from ..credentials import TrelloCredentials
from tracardi.service.storage.driver import storage
from tracardi.process_engine.action.v1.connectors.trello.trello_client import TrelloClient


async def validate(config: dict) -> Config:
    plugin_config = Config(**config)
    credentials = TrelloCredentials(
        **(await storage.driver.resource.load(plugin_config.source.id)).credentials.production
    )
    client = TrelloClient(credentials.api_key, credentials.token)
    plugin_config.list_id = await client.get_list_id(plugin_config.board_url, plugin_config.list_name)
    return plugin_config


class TrelloMemberAdder(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'TrelloMemberAdder':
        config = Config(**kwargs)
        credentials = TrelloCredentials(
            **(await storage.driver.resource.load(config.source.id)).credentials.production
        )
        client = TrelloClient(credentials.api_key, credentials.token)
        return TrelloMemberAdder(client, config)

    def __init__(self, client: TrelloClient, config: Config):
        self._client = client
        self.config = config

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        self.config.member_id = dot[self.config.member_id]
        self.config.card_name = dot[self.config.card_name]

        try:
            result = await self._client.add_member(self.config.list_id, self.config.card_name, self.config.member_id)
        except (ConnectionError, ValueError) as e:
            self.console.error(str(e))
            return Result(port="error", value=payload)

        return Result(port="response", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='TrelloMemberAdder',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "board_url": None,
                "list_name": None,
                "member_id": None
            },
            manual="trello/add_trello_member_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Trello resource",
                                description="Please select your Trello resource.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "trello"})
                            ),
                            FormField(
                                id="board_url",
                                name="URL of Trello board",
                                description="Please provide the URL of your board.",
                                component=FormComponent(type="text", props={"label": "Board URL"})
                            ),
                            FormField(
                                id="list_name",
                                name="Name of Trello list",
                                description="Please provide the name of your Trello list.",
                                component=FormComponent(type="text", props={"label": "List name"})
                            ),
                            FormField(
                                id="card_name",
                                name="Name of your card",
                                description="Please provide path to the name of the card that you want to add member "
                                            "to.",
                                component=FormComponent(type="dotPath", props={"label": "Card name", "defaultMode": "2"})
                            ),
                            FormField(
                                id="member_id",
                                name="ID of the member",
                                description="Please provide the path to the field containing ID of the member that you "
                                            "want to add.",
                                component=FormComponent(type="dotPath", props={"label": "ID of the member", "defaultMode": "2"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Add Trello member',
            desc='Adds a member to given card on given list in Trello.',
            icon='trello',
            group=["Trello"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns a response from Trello API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
