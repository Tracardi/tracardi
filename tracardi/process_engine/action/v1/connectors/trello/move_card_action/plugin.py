from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.driver import storage
from tracardi.process_engine.action.v1.connectors.trello.trello_client import TrelloClient
from ..credentials import TrelloCredentials


async def validate(config: dict) -> Config:
    plugin_config = Config(**config)
    credentials = TrelloCredentials(
        **(await storage.driver.resource.load(plugin_config.source.id)).credentials.production
    )
    client = TrelloClient(credentials.api_key, credentials.token)
    list_id1 = await client.get_list_id(plugin_config.board_url, plugin_config.list_name1)
    list_id2 = await client.get_list_id(plugin_config.board_url, plugin_config.list_name2)
    plugin_config = Config(**plugin_config.dict(exclude={"list_id1", "list_id2"}), list_id1=list_id1, list_id2=list_id2)
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
        self._client.set_retries(self.node.on_connection_error_repeat)
        self.config = config

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        card_name = dot[self.config.card_name]

        try:
            result = await self._client.move_card(self.config.list_id1, self.config.list_id2, card_name)
        except (ConnectionError, ValueError) as e:
            self.console.error(str(e))
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
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            manual="trello/move_trello_card_action"
        ),
        metadata=MetaData(
            name='Move Trello card',
            desc='Moves card from given list on given board to another list on that board in Trello.',
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
            ),
            pro=True
        )
    )
