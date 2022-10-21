from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from pydantic import validator
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    script_url: str

    @validator("script_url")
    def validate_file_path(cls, value):
        if value == "":
            raise ValueError("Script URL can not be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class ZendeskWidgetPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        self.ux.append({
            "tag": "script",
            "props": {"src": self.config.script_url, "id": "ze-snippet"}
        })
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ZendeskWidgetPlugin',
            brand="Zendesk",
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.3',
            license="MIT",
            author="Risto Kowaczewski",
            manual="zendesk_widget_action",
            init={
                "script_url": "https://static.zdassets.com/ekr/snippet.js?key=<your-key>",
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Zendesk widget configuration",
                        fields=[
                            FormField(
                                id="script_url",
                                name="Zendesk script URL",
                                description="The URL is displayed when you open an account in Zendesk. "
                                            "Please see the zendesk.com documentation for more details.",
                                component=FormComponent(type="text", props={"label": "Script URL"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Zendesk widget',
            desc='Shows Zendesk widget on the webpage.',
            icon='zendesk',
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
