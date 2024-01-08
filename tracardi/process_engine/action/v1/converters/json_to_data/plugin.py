import json

from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from .model.models import Configuration


def validate(config: dict):
    return Configuration(**config)


class JsonToObjectAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        json_string = dot[self.config.to_data]
        try:
            result = json.loads(json_string)
            return Result(port="payload", value={"value": result})
        except json.JSONDecodeError:
            return Result(port="error", value={"value": payload})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='JsonToObjectAction',
            inputs=["payload"],
            outputs=['payload', "error"],
            version='0.6.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "to_data": None
            },
            form=Form(groups=[
                FormGroup(
                    name="Convert JSON string to data",
                    fields=[
                        FormField(
                            id="to_data",
                            name="Reference path",
                            description="Reference path to JSON string to be converted"
                                        "E.g. profile@stats.counters.boughtProducts",
                            component=FormComponent(type="dotPath", props={"label": "Reference path",
                                                                           "defaultSourceValue": "event"})
                        )
                    ]
                )
            ]),
        ),
        metadata=MetaData(
            name='JSON to data',
            desc='Converts JSON to data objects',
            icon='json',
            group=["Converters"],
            tags=['json', 'object']
        )
    )
