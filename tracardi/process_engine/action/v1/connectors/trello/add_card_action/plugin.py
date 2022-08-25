from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from .model.config import Config, Card
from ..credentials import TrelloCredentials
from tracardi.service.storage.driver import storage
from tracardi.process_engine.action.v1.connectors.trello.trello_client import TrelloClient
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.notation.dot_template import DotTemplate
from ..trello_plugin import TrelloPlugin


async def validate(config: dict) -> Config:
    plugin_config = Config(**config)
    credentials = TrelloCredentials(
        **(await storage.driver.resource.load(plugin_config.source.id)).credentials.production
    )
    client = TrelloClient(credentials.api_key, credentials.token)
    list_id = await client.get_list_id(plugin_config.board_url, plugin_config.list_name)
    plugin_config = Config(**plugin_config.dict(exclude={"list_id"}), list_id=list_id)
    return plugin_config


class TrelloCardAdder(TrelloPlugin):
    config: Config

    async def set_up(self, init):
        self.config = Config(**init)
        await self.set_up_trello(self.config)

    async def run(self, payload: dict, in_edge=None) -> Result:
        self._client.set_retries(self.node.on_connection_error_repeat)
        dot = self._get_dot_accessor(payload)
        coords = dot[self.config.card.coordinates]
        coords = f"{coords['latitude']}," \
                                       f"{coords['longitude']}" if isinstance(coords, dict) else coords

        traverser = DictTraverser(dot)
        card = Card(**traverser.reshape(self.config.card.dict()))

        template = DotTemplate()
        card.desc = template.render(self.config.card.desc, dot)
        card.due = str(dot[self.config.card.due]) if self.config.card.due is not None else None
        card.coordinates = coords

        try:
            result = await self._client.add_card(self.config.list_id, **card.dict())
        except (ConnectionError, ValueError) as e:
            self.console.error(str(e))
            return Result(port="error", value=payload)

        return Result(port="response", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='TrelloCardAdder',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            manual="trello/add_trello_card_action"
        ),
        metadata=MetaData(
            name='Add Trello card',
            desc='Adds card to given list on given board in Trello.',
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
