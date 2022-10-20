from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from pydantic import validator
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    license: str

    @validator("license")
    def validate_file_path(cls, value):
        if value == "":
            raise ValueError("License can not be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class LivechatWidgetPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        self.ux.append({
            "tag": "script",
            "props": {"src": f'http://localhost:8686/livechat/{self.config.license}'}
        })
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='LivechatWidgetPlugin',
            brand="livechat",
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.3',
            license="MIT",
            author="Risto Kowaczewski",
            manual="livechat_widget_action",
            init={
                "license": ""
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Livechat widget configuration",
                        fields=[
                            FormField(
                                id="license",
                                name="Your LiveChat license number",
                                component=FormComponent(type="text", props={"label": "License"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='LiveChat widget',
            desc='Shows LiveChat widget on the webpage.',
            icon='livechat',
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
