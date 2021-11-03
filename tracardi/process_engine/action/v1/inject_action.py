import json
from json import JSONDecodeError
from typing import Dict, Union

from pydantic import BaseModel, validator
from tracardi_dot_notation.dict_traverser import DictTraverser
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class Configuration(BaseModel):
    value: Union[str, Dict] = ""

    @validator("value")
    def validate_content(cls, value):
        try:
            # Try parsing JSON
            return json.loads(value)
        except JSONDecodeError as e:
            raise ValueError(str(e))


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class InjectAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
        converter = DictTraverser(self._get_dot_accessor(payload))
        return Result(value=converter.reshape(self.config.value), port="payload")


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=True,
        spec=Spec(
            module='tracardi.process_engine.action.v1.inject_action',
            className='InjectAction',
            inputs=[],
            outputs=["payload"],
            init={"value": ""},
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
            manual='inject_action',
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Inject',
            desc='Injector.',
            keywords=['start node'],
            type='flowNode',
            width=100,
            height=100,
            icon='json',
            group=["Input/Output"]
        )
    )
