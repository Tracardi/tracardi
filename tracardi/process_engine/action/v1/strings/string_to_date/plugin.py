from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner

from model.configuration import Configuration
from datetime import datetime
import dateparser

def validate(config: dict) -> Configuration:
    return Configuration(**config)


class DateConverter(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        date_string = payload.get(self.config.string)


        if date_string:
            try:
                converted_date = dateparser.parse(date_string).date().strftime("%Y-%m-%d")
                payload[self.config.replace_with] = converted_date
            except ValueError:
                pass
        return Result(port="payload", value=payload)


def register() -> Plugin:
    plugin = Plugin(
        start=False,
        spec=Spec(
            module='action.v1.strings.string_to_date.plugin',
            className='DateConverter',
            inputs=["payload"],
            outputs=["payload"],
            version='0.1',
            license="MIT",
            author="Kaushik Iyer",
            init={
                "string": None,
                "format": None,
                "replace_with": None
            },
            manual="string_to_date_action",
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="string",
                            name="String",
                            description="Please provide a path to the text (or the text itself) that you want to convert",
                            component=FormComponent(type="dotPath", props={"defaultSourceValue": "event"})
                        ),
                        FormField(
                            id="format",
                            name="Format",
                            description="Please provide the format of the date",
                            component=FormComponent(type="text", props={"label": "Format"})
                        ),
                        FormField(
                            id="replace_with",
                            name="Replace with",
                            description="Please provide the path to the event where the converted date will be stored",
                            component=FormComponent(type="dotPath", props={"defaultSourceValue": "event"})
                        )
                    ]
                )
            ]),
        ),
        metadata=MetaData(
            name='Date converter',
            desc='Converts string to date',
            type='flowNode',
            icon='date',
            group=["Transform"],
        )
    )
