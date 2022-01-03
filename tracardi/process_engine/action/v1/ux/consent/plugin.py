from pydantic import BaseModel, validator

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


# class Configuration(BaseModel):
#     message: str
#
#     @validator("message")
#     def should_no_be_empty(cls, value):
#         if len(value) == 0:
#             raise ValueError("Message should not be empty")
#         return value
#
#
# def validate(config: dict):
#     return Configuration(**config)


class ConsentUx(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload):

        self.ux.append({"tag": "div", "props": { "class": "tracardi-uix-consent"}})
        self.ux.append({"tag": "script", "props": {"src": "src/widgets/drawer/index.js"}})

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ConsentUx',
            inputs=["payload"],
            outputs=["payload"],
            init={
                "enable": True
            },
            version='0.6.0.1',
            license="MIT",
            author="Risto Kowaczewski",
            # form=Form(groups=[
            #     FormGroup(
            #         name="Message",
            #         fields=[
            #             FormField(
            #                 id="message",
            #                 name="Pop-up message",
            #                 description="Provide message that will be show on the web page.",
            #                 component=FormComponent(type="textarea", props={"label": "message"})
            #             )
            #         ]
            #     ),
            # ]),

        ),
        metadata=MetaData(
            name='Show consent bar',
            desc='Shows consent pop-up on the front end.',
            icon='react',
            group=["UI Widgets"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"payload": PortDoc(desc="This port returns input payload object.")}
            )
        )
    )
