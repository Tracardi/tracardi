from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from pydantic import validator
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    api_url: str
    token: str

    @validator("api_url")
    def validate_api_url(cls, value):
        if value == "":
            raise ValueError("Api URL can not be empty.")
        return value

    @validator("token")
    def validate_file_path(cls, value):
        if value == "":
            raise ValueError("Token can not be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class ChatwootWidgetPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        self.ux.append({
            "tag": "script",
            "props": {"src": f'{self.config.api_url}/chatwoot/{self.config.token}'}
        })
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ChatwootWidgetPlugin',
            brand="Chatwoot",
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.3',
            license="MIT",
            author="Risto Kowaczewski",
            manual="chatwoot_widget_action",
            init={
                "api_url": "http://localhost:8686",
                "license": ""
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Livechat widget configuration",
                        fields=[
                            FormField(
                                id="api_url",
                                name="Your Tracardi API URL",
                                component=FormComponent(type="text", props={"label": "Tracardi API URL"})
                            ),
                            FormField(
                                id="token",
                                name="Your Chatwoot token",
                                description="If you do not know you token please login to chatwoot.com and go to settings/inboxes adn look for the javascript .",
                                component=FormComponent(type="text", props={"label": "Chatwoot token"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Chatwoot widget',
            desc='Shows Chatwoot widget on the webpage.',
            icon='chatwoot',
            tags=['messaging', 'chat'],
            group=["UIX Widgets"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload without any changes.")
                }
            )
        )
    )
