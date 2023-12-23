from tracardi.service.utils.date import now_in_utc

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config
from datetime import datetime, timedelta
from dateutil import parser
from dateutil.parser import ParserError


def validate(config: dict):
    return Config(**config)


class TimeDelay(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    @staticmethod
    def parse_date(date):
        try:
            if isinstance(date, str):
                if date == 'now':
                    date = now_in_utc()
                else:
                    date = parser.parse(date)
            elif not isinstance(date, datetime):
                raise ValueError("Date can be either string or datetime object")
            return date
        except ParserError:
            raise ValueError("Could not parse data `{}`".format(date))

    async def run(self, payload: dict, in_edge=None) -> Result:

        try:

            dot = self._get_dot_accessor(payload)

            ref_date = self.parse_date(dot[self.config.reference_date])

            if self.config.sign == "+":
                new_date = ref_date + timedelta(seconds=int(self.config.delay))
            else:
                new_date = ref_date - timedelta(seconds=int(self.config.delay))

            return Result(port="date", value={
                "date": new_date
            })

        except Exception as e:
            return Result(port="error", value={
                "message": str(e)
            })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='TimeDelay',
            inputs=["payload"],
            outputs=["date", "error"],
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='time_delay',
            init={
                "reference_date": "profile@metadata.time.insert",
                "sign": "+",
                "delay": "60"
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Time delta",
                        description="Calculates the time difference between two dates.",
                        fields=[
                            FormField(
                                id="reference_date",
                                name="Reference date",
                                description="Please type path to the date.",
                                component=FormComponent(type="dotPath", props={
                                    "label": "Date"
                                }),
                                required=True
                            ),
                            FormField(
                                id="sign",
                                name="Operation",
                                description="Please select if you would like to add delay or subtract delay.",
                                component=FormComponent(type="select", props={
                                    "label": "Operation",
                                    "items": {
                                        "+": "Add",
                                        "-": "Subtract"
                                    }
                                }),
                                required=True
                            ),
                            FormField(
                                id="delay",
                                name="A delay in seconds",
                                description="Please type delay that will be added to the reference date.",
                                component=FormComponent(type="text", props={"label": "Delay"}),
                                required=True
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Time delay',
            desc='Returns date plus the defined delay.',
            type='flowNode',
            icon='time',
            group=["Time"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port payload object.")
                },
                outputs={
                    "date": PortDoc(desc="This port returns a date."),
                    "error": PortDoc(desc="This port returns an error.")
                }
            )
        )
    )
