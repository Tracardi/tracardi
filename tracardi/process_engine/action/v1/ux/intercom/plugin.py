from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from pydantic import validator
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    api_url: str
    app_id: str

    @validator("api_url")
    def validate_api_url(cls, value):
        if value is None:
            raise ValueError("Api URL can not be empty.")
        return value

    @validator("app_id")
    def validate_file_path(cls, value):
        if value is None:
            raise ValueError("Application ID can not be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class IntercomWidgetPlugin(ActionRunner):
    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        self.ux.append({
            "tag": "script",
            "props": {"src": f'{self.config.api_url}/intercom/{self.config.app_id}'}
        })

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='IntercomWidgetPlugin',
            brand="intercom",
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.3',
            license="MIT",
            author="Mateusz Zitaruk",
            manual="intercom_widget_action",
            init={
                "api_url": "http://localhost:8686",
                "app_id": ""
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Intercom widget configuration",
                        fields=[
                            FormField(
                                id="api_url",
                                name="Your Tracardi API URL",
                                component=FormComponent(type="text", props={"label": "Tracardi API URL"})
                            ),
                            FormField(
                                id="app_id",
                                name="Your Intercom application ID",
                                component=FormComponent(type="text", props={"label": "Application ID"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Intercom widget',
            desc='Shows Intercom widget on the webpage.',
            icon='intercom',
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
