from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner

from .model.configuration import Configuration
import dateparser


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class DateConverter(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload)
        date_string = dot[self.config.string]

        if date_string:
            try:
                converted_date = dateparser.parse(date_string).date()
                return Result(port="date", value={"date": converted_date})
            except Exception as e:
                return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.strings.string_to_date.plugin',
            className=DateConverter.__name__,
            inputs=["payload"],
            outputs=["payload", "error"],
            version='0.8.2',
            license="MIT + CC",
            author="Kaushik Iyer, Risto Kowaczewski",
            init={
                "string": ""
            },
            manual="string_to_date_action",
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="string",
                            name="String",
                            description="Please provide a path to the text (or the text itself) that you want to convert.",
                            component=FormComponent(type="dotPath", props={"defaultSourceValue": "event"})
                        )
                    ]
                )
            ]),
        ),
        metadata=MetaData(
            name='String to date',
            desc='Converts string to date',
            type='flowNode',
            icon='date',
            group=["Transform"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload.")
                },
                outputs={
                    "date": PortDoc(desc="Returns data object."),
                    "error": PortDoc(desc="Returns error message."),
                }
            )
        )
    )
