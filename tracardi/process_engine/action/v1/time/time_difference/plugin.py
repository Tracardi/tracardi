from parser import ParserError

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from .model.config import Config
from datetime import datetime
from dateutil import parser


def validate(config: dict):
    return Config(**config)


class TimeDiffCalculator(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    @staticmethod
    def parse_date(date):
        try:
            if isinstance(date, str):
                if date == 'now':
                    date = datetime.utcnow()
                else:
                    date = parser.parse(date)
            elif not isinstance(date, datetime):
                raise ValueError("Date can be either string or datetime object")
            return date
        except ParserError:
            raise ValueError("Could not parse data `{}`".format(date))

    async def run(self, payload):

        dot = self._get_dot_accessor(payload)

        ref_date = self.parse_date(dot[self.config.reference_date])
        now_date = self.parse_date(dot[self.config.now])

        diff_secs = (now_date - ref_date).total_seconds()

        return Result(port="time_difference", value={
            "seconds": diff_secs,
            "minutes": diff_secs / 60,
            "hours": diff_secs / (60 * 60),
            "days": diff_secs / (60 * 60 * 24),
            "weeks": diff_secs / (60 * 60 * 24 * 7)
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.time.time_difference.plugin',
            className='TimeDiffCalculator',
            inputs=["payload"],
            outputs=["time_difference"],
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk",
            init={
                "reference_date": None,
                "now": "now"
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Time data",
                        description="Please provide path to date, which will be considered the reference date for "
                                    "calculations, and so called 'now' date, in one of available forms.",
                        fields=[
                            FormField(
                                id="reference_date",
                                name="Reference date",
                                component=FormComponent(type="dotPath", props={
                                    "label": "Source"
                                }),
                                required=True
                            ),
                            FormField(
                                id="now",
                                name="Second date",
                                description="Please provide path, date or 'now' parameter, "
                                            "according to format chosen above.",
                                component=FormComponent(type="dotPath", props={"label": "Source"}),
                                required=True
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Time difference',
            desc='Returns time difference between two dates.',
            type='flowNode',
            icon='time',
            group=["Time"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port payload object.")
                },
                outputs={
                    "time_difference": PortDoc(desc="This port returns time difference in several time "
                                                    "units.")
                }
            )
        )
    )
