from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from .model.config import Config, TrelloCredentials, Card
from tracardi.service.storage.driver import storage
from tracardi.process_engine.action.v1.connectors.trello.trello_client import TrelloClient
from tracardi_dot_notation.dict_traverser import DictTraverser
from fastapi import HTTPException
from tracardi_dot_notation.dot_template import DotTemplate


async def validate(config: dict) -> Config:
    plugin_config = Config(**config)
    credentials = TrelloCredentials(
        **(await storage.driver.resource.load(plugin_config.source.id)).credentials.production
    )
    client = TrelloClient(credentials.api_key, credentials.token)
    plugin_config.list_id = await client.get_list_id(plugin_config.board_url, plugin_config.list_name)
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

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        coords = dot[self.config.card.coordinates]
        self.config.card.coordinates = f"{coords['latitude']}," \
                                       f"{coords['longitude']}" if isinstance(coords, dict) else coords

        self.config.card.due = str(dot[self.config.card.due]) if self.config.card.due is not None else None

        traverser = DictTraverser(dot)
        self.config.card = Card(**traverser.reshape(self.config.card.dict()))

        template = DotTemplate()
        self.config.card.desc = template.render(self.config.card.desc, dot)

        try:
            result = await self._client.add_card(self.config.list_id, **self.config.card.dict())
        except (HTTPException, ValueError):
            return Result(port="error", value={})

        return Result(port="response", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='TrelloCardAdder',
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
                "list_name": None,
                "card": {
                    "name": None,
                    "desc": None,
                    "urlSource": None,
                    "coordinates": None,
                    "due": None
                }

            },
            # manual="",
            form=Form(
                name="Plugin configuration",
                groups=[
                    FormGroup(
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
                                description="Please the URL of your board.",
                                component=FormComponent(type="text", props={"label": "Board URL"})
                            ),
                            FormField(
                                id="list_name",
                                name="Name of Trello list",
                                description="Please provide the name of your Trello list. You don't have to look for"
                                            "it's ID. Tracardi will do this for you.",
                                component=FormComponent(type="text", props={"label": "List name"})
                            ),
                            FormField(
                                id="card.name",
                                name="Name of your card",
                                description="Please provide path to the name of the card that you want to add.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="card.desc",
                                name="Card description",
                                description="Please provide description of your card. It's fully functional in terms of"
                                            " using templates.",
                                component=FormComponent(type="textarea", props={"label": "Card description"})
                            ),
                            FormField(
                                id="card.urlSource",
                                name="Card link",
                                description="You can add an URL to your card as an attachment.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="card.coordinates",
                                name="Card coordinates",
                                description="You can add location coordinates to your card. This should be a path"
                                            " to an object, containing 'longitude' and 'latitude' fields.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="card.due",
                                name="Card due date",
                                description="You can add due date to your card. Various formats should work, but "
                                            "UTC format seems to be the best option.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Add Trello card',
            desc='Adds card to given list on given board in Trello.',
            type='flowNode',
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
