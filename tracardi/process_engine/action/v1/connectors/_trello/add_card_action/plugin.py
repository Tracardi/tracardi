from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
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
            manual="trello/add_trello_card_action",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "board_url": "",
                "list_name": "",
                "card": {
                    "name": "",
                    "desc": "",
                    "urlSource": "",
                    "coordinates": "",
                    "due": ""
                }

            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Trello resource",
                                description="Please select your Trello resource.",
                                component=FormComponent(type="resource",
                                                        props={"label": "Resource", "tag": "trello"})
                            ),
                            FormField(
                                id="board_url",
                                name="URL of Trello board",
                                description="Please the URL of your board.",
                                component=FormComponent(type="text", props={"label": "Board URL"})
                            ),
                            FormField(
                                id="list_name",
                                name="Name of Trello list",
                                description="Please provide the name of your Trello list.",
                                component=FormComponent(type="text", props={"label": "List name"})
                            ),
                            FormField(
                                id="card.name",
                                name="Name of your card",
                                description="Please provide path to the name of the card that you want to add.",
                                component=FormComponent(type="dotPath", props={"label": "Card name",
                                                                               "defaultMode": "2"})
                            ),
                            FormField(
                                id="card.desc",
                                name="Card description",
                                description="Please provide description of your card. It's fully functional in terms of"
                                            " using templates.",
                                component=FormComponent(type="textarea",
                                                        props={"label": "Card description"})
                            ),
                            FormField(
                                id="card.urlSource",
                                name="Card link",
                                description="You can add an URL to your card as an attachment.",
                                component=FormComponent(type="dotPath", props={"label": "Card link",
                                                                               "defaultMode": "2"})
                            ),
                            FormField(
                                id="card.coordinates",
                                name="Card coordinates",
                                description="You can add location coordinates to your card. This should be a path"
                                            " to an object, containing 'longitude' and 'latitude' fields.",
                                component=FormComponent(type="dotPath",
                                                        props={"label": "Card coordinates",
                                                               "defaultMode": "2"})
                            ),
                            FormField(
                                id="card.due",
                                name="Card due date",
                                description="You can add due date to your card. Various formats should work, but "
                                            "UTC format seems to be the best option.",
                                component=FormComponent(type="dotPath",
                                                        props={"defaultMode": "2",
                                                               "label": "Card due date"})
                            )
                        ]
                    )
                ]
            )
        ),
        # todo this may be not need
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
