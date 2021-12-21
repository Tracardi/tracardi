from parser import ParserError

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from .model.config import Config
from datetime import datetime
from dateutil import parser
from math import copysign


def validate(config: dict):
    return Config(**config)


class TimeDiffCalculator(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    @staticmethod
    def parse_date(date):
        try:
            if isinstance(date, str):
                date = parser.parse(date)
            return date
        except ParserError as e:
            raise ValueError("Could not parse data `{}`".format(date))

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        ref_date = datetime.utcnow()
        if self.config.reference_date_format == "date":
            ref_date = self.parse_date(self.config.reference_date)
        elif self.config.now_format == "path":
            ref_date = self.parse_date(dot[self.config.reference_date])
        now_date = datetime.utcnow()
        if self.config.now_format == "date":
            now_date = self.parse_date(self.config.now)
        elif self.config.now_format == "path":
            now_date = self.parse_date(dot[self.config.now])
        diff_secs = int((now_date - ref_date).total_seconds())
        sign = copysign(1, diff_secs)
        diff_secs = abs(diff_secs)
        return Result(port="time_difference", value={
            "seconds": sign * diff_secs,
            "minutes": sign * (diff_secs//60),
            "hours": sign * (diff_secs//(60*60)),
            "days": sign * (diff_secs//(60*60*24)),
            "weeks": sign * (diff_secs//(60*60*24*7))
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.time.time_difference.plugin',
            className='TimeDiffCalculator',
            inputs=["payload"],
            outputs=["time_difference"],
            version='0.6.0.2',
            license="MIT",
            author="Dawid Kruk",
            init={
                "reference_date_format": "now",
                "reference_date": "now",
                "now_format": "now",
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
                                id="reference_date_format",
                                name="Format of reference date",
                                description="This field defines type of date that is considered as the lower bound "
                                            "of calculated time span. "
                                            "Now requires 'now' value in reference date field. "
                                            "Date requires date in reference date field "
                                            "(Example: 2021-03-14). "
                                            "Path requires path to wanted date (Example: event@metadata.time.insert).",
                                component=FormComponent(type="select", props={
                                    "items": {
                                        "now": "Now",
                                        "date": "Date",
                                        "path": "Path"
                                    },
                                    "label": "Format"
                                }),
                                required=True
                            ),
                            FormField(
                                id="reference_date",
                                name="Reference date",
                                component=FormComponent(type="dotPath", props={
                                    "label": "Source"
                                }),
                                required=True
                            ),
                            FormField(
                                id="now_format",
                                name="Format of second date",
                                description="This field defines type of date that is considered as the upper bound "
                                            "of calculated time span. "
                                            "Now requires 'now' value in second date field. "
                                            "Date requires date in second date field "
                                            "(Example: 2021-03-14). "
                                            "Path requires path to wanted date (Example: event@metadata.time.insert).",
                                component=FormComponent(type="select", props={
                                    "items": {
                                        "now": "Now",
                                        "date": "Date",
                                        "path": "Path"
                                    },
                                    "label": "Format"
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
            desc='Calculates time difference between given dates and returns it in multiple units.',
            type='flowNode',
            icon='time',
            group=["Time"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "time_difference": PortDoc(desc="This port returns calculated time difference in multiple time "
                                                    "units.")
                }
            )
        )
    )
