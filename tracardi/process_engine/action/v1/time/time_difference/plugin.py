from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from .model.config import Config
from tracardi_dot_notation.dot_accessor import DotAccessor
from datetime import datetime
from dateutil import parser


def validate(config: dict):
    return Config(**config)


class TimeDiffCalculator(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
        dot = DotAccessor(profile=self.profile, session=self.session, payload=payload, event=self.event, flow=self.flow)
        ref_date = dot[self.config.reference_date]
        now_date = datetime.utcnow()
        if self.config.now_format == "date":
            now_date = parser.parse(self.config.now)
        elif self.config.now_format == "path":
            now_date = dot[self.config.now]
        diff_secs = int((now_date - ref_date).total_seconds())
        return Result(port="payload", value=payload), Result(port="time_difference", value={
            "seconds": diff_secs,
            "minutes": diff_secs//60,
            "hours": diff_secs//(60*60),
            "days": diff_secs//(60*60*24),
            "weeks": diff_secs//(60*60*24*7)
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.time.time_difference.plugin',
            className='TimeDiffCalculator',
            inputs=["payload"],
            outputs=["payload", "time_difference"],
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk",
            init={
                "reference_date": "<path-to-reference-date>",
                "now_format": "path | date | now",
                "now": "profile@metadata.time.update | 2021-01-01 | now"
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
                                    "label": "Prefix"
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
                                component=FormComponent(type="text", props={"label": "Date in chosen format"}),
                                required=True
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Calculate Time Diff',
            desc='Calculates time difference between given dates and returns it in multiple units.',
            type='flowNode',
            icon='plugin',
            group=["Time"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "time_difference": PortDoc(desc="This port returns calculated time difference in multiple time "
                                                    "units."),
                    "payload": PortDoc(desc="This port returns given payload without any changes.")
                }
            )
        )
    )
