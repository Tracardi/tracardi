import json
from json import JSONDecodeError
from typing import Dict, Union
from pydantic import BaseModel, validator
from tracardi_dot_notation.dict_traverser import DictTraverser
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class Configuration(BaseModel):
    value: str = ""

    @validator("value")
    def validate_content(cls, value):
        try:
            if isinstance(value, dict):
                value = json.dumps(value)
            return value

        except JSONDecodeError as e:
            raise ValueError(str(e))


def validate(config: dict) -> Configuration:
    config = Configuration(**config)

    # Try parsing JSON just for validation purposes
    try:
        json.loads(config.value)
    except JSONDecodeError as e:
        raise ValueError(str(e))

    return config


class ReshapePayloadAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Configuration(**kwargs)

    async def run(self, payload):
        if not isinstance(payload, dict):
            self.console.warning("Payload is not dict that is why you will not be able to read it. ")

        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        template = DictTraverser(dot)
        output = json.loads(self.config.value)
        result = template.reshape(reshape_template=output)

        return Result(port="payload", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.reshape_payload_action',
            className='ReshapePayloadAction',
            inputs=["payload"],
            outputs=['payload'],
            init={"value": "{}"},
            form=Form(groups=[
                FormGroup(
                    name="Create payload object",
                    fields=[
                        FormField(
                            id="value",
                            name="Object to inject",
                            description="Provide object as JSON to be injected into payload and returned "
                                        "on output port.",
                            component=FormComponent(type="json", props={"label": "object"})
                        )
                    ]
                ),
            ]),
            manual="reshape_payload_action",
            version='0.6.0',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Make payload',
            desc='Creates new payload from provided data. Configuration defines where the data should be copied.',
            icon='copy-property',
            group=["Data processing"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns new payload,formed from given payload"
                                            " according to configuration.")
                }
            )
        )
    )
