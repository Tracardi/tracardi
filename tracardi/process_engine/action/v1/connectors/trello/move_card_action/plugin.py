from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from .model.config import Config, TrelloCredentials
from tracardi.service.storage.driver import storage
from tracardi.process_engine.action.v1.connectors.trello.trello_client import TrelloClient
from fastapi import HTTPException


async def validate(config: dict) -> Config:
    plugin_config = Config(**config)
    credentials = TrelloCredentials(
        **(await storage.driver.resource.load(plugin_config.source.id)).credentials.production
    )
    client = TrelloClient(credentials.api_key, credentials.token)
    plugin_config.list_id1 = await client.get_list_id(plugin_config.board_url, plugin_config.list_name1)
    plugin_config.list_id2 = await client.get_list_id(plugin_config.board_url, plugin_config.list_name2)
    return plugin_config


class TrelloCardMover(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'TrelloCardMover':
        config = Config(**kwargs)
        credentials = TrelloCredentials(
            **(await storage.driver.resource.load(config.source.id)).credentials.production
        )
        client = TrelloClient(credentials.api_key, credentials.token)
        return TrelloCardMover(client, config)

    def __init__(self, client: TrelloClient, config: Config):
        self._client = client
        self.config = config

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        self.config.card_name = dot[self.config.card_name]

        try:
            result = await self._client.move_card(self.config.list_id1, self.config.list_id2, self.config.card_name)
        except (HTTPException, ValueError):
            return Result(port="error", value={})

        return Result(port="response", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='TrelloCardMover',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "board_url": None,
                "list_name1": None,
                "list_name2": None,
                "card_name": None
            },
            # manual="",
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
                                id="list_name1",
                                name="Name of current Trello list",
                                description="Please provide the name of your Trello list that card is currently on.",
                                component=FormComponent(type="text", props={"label": "List name"})
                            ),
                            FormField(
                                id="list_name2",
                                name="Name of target Trello list",
                                description="Please provide the name of your Trello list that you want to move your "
                                            "card to.",
                                component=FormComponent(type="text", props={"label": "List name"})
                            ),
                            FormField(
                                id="card_name",
                                name="Name of your card",
                                description="Please provide path to the name of the card that you want to delete.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Move Trello card',
            desc='Moves card from given list on given board to another list on that board in Trello.',
            icon='trello',
            group=["Connectors"],
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
