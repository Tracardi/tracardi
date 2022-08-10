from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, Card
from ..credentials import TrelloCredentials
from tracardi.service.storage.driver import storage
from tracardi.process_engine.action.v1.connectors.trello.trello_client import TrelloClient
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.notation.dot_template import DotTemplate


async def validate(config: dict) -> Config:
    plugin_config = Config(**config)
    credentials = TrelloCredentials(
        **(await storage.driver.resource.load(plugin_config.source.id)).credentials.production
    )
    client = TrelloClient(credentials.api_key, credentials.token)
    list_id = await client.get_list_id(plugin_config.board_url, plugin_config.list_name)
    plugin_config = Config(**plugin_config.dict(exclude={"list_id"}), list_id=list_id)
    return plugin_config


class TrelloCardAdder(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'TrelloCardAdder':
        config = Config(**kwargs)
        credentials = TrelloCredentials(
            **(await storage.driver.resource.load(config.source.id)).credentials.production
        )
        client = TrelloClient(credentials.api_key, credentials.token)
        return TrelloCardAdder(client, config)

    def __init__(self, client: TrelloClient, config: Config):
        self._client = client
        self.config = config

    async def run(self, payload: dict, in_edge=None) -> Result:
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
