import json

from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from .model.models import Configuration


def validate(config: dict):
    return Configuration(**config)


class ConvertAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        path = dot[self.config.to_json]

        result = json.dumps(dict(path), default=str)

        return Result(port="payload", value={"json": result})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.converters.payload_to_json.plugin',
            className='ConvertAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.0.1',
            license="MIT",
            author="Patryk Migaj",
            init={
                "to_json": None
            },
            form=Form(groups=[
                FormGroup(
                    name="Convert data to JSON string",
                    fields=[
                        FormField(
                            id="to_json",
                            name="Path to data",
                            description="Path to data to be serialized to JSON. "
                                        "E.g. profile@stats.counters.boughtProducts",
                            component=FormComponent(type="dotPath", props={"label": "Field path"})
                        )
                    ]
                )
            ]),
        ),
        metadata=MetaData(
            name='To JSON',
            desc='This plugin converts objects to JSON',
            icon='json',
            group=["Data processing"]
        )
    )
