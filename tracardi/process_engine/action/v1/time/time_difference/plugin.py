from tracardi.service.utils.date import now_in_utc

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config
from datetime import datetime
from dateutil import parser
from dateutil.parser import ParserError


def validate(config: dict):
    return Config(**config)


class TimeDiffCalculator(ActionRunner):

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
            license="MIT + CC",
            author="Dawid Kruk, Risto Kowaczewski",
            manual='time_difference',
            init={
                "reference_date": None,
                "now": "now"
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
                                description="Please type path to the start date.",
                                component=FormComponent(type="dotPath", props={
                                    "label": "Source"
                                }),
                                required=True
                            ),
                            FormField(
                                id="now",
                                name="Second date",
                                description="Please type path, date or 'now'. This is the end date.",
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
            purpose=['collection', 'segmentation'],
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
