import json

from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from .model.models import Configuration


def validate(config: dict):
    return Configuration(**config)


class ObjectToJsonAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        path = dot[self.config.to_json]

        result = json.dumps(dict(path), default=str)

        return Result(port="payload", value={"json": result})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ObjectToJsonAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.0.1',
            license="MIT + CC",
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
                            name="Reference path to data",
                            description="Reference path to data to be serialized to JSON. "
                                        "E.g. profile@stats.counters.boughtProducts",
                            component=FormComponent(type="dotPath", props={"label": "Field path",
                                                                           "defaultSourceValue": "event"})
                        )
                    ]
                )
            ]),
        ),
        metadata=MetaData(
            name='Data to JSON',
            desc='This plugin converts objects to JSON',
            icon='json',
            group=["Converters"],
            tags=['json', 'object']
        )
    )
