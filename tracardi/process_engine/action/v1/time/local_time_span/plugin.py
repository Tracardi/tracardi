import re
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.configuration import TimeSpanConfiguration


def validate(config: dict) -> TimeSpanConfiguration:
    return TimeSpanConfiguration(**config)


class LocalTimeSpanAction(ActionRunner):

    config: TimeSpanConfiguration

    async def set_up(self, init):
        self.config = validate(init)

    @staticmethod
    def _validate_timezone(timezone):
        regex = re.compile(r'^[a-zA-z\-]+\/[a-zA-z\-]+$', re.I)
        return regex.match(str(timezone))

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        time_zone = dot[self.config.timezone]

        if not self._validate_timezone(time_zone):
            raise ValueError("Your configuration {} points to value {}. And the value is not valid time zone.".format(
                self.config.timezone, time_zone
            ))

        if self.config.is_in_timespan():
            return Result(value=payload, port="in")

        return Result(value=payload, port="out")


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.time.local_time_span.plugin',
            className='LocalTimeSpanAction',
            inputs=['payload'],
            outputs=['in', 'out'],
            manual='local_time_span_action',
            version="0.6.0.1",
            author="Marcin Gaca, Risto Kowaczewski",
            init={
                "timezone": "session@context.time.tz",
                "start": None,
                "end": None,
            },
            form=Form(groups=[
                FormGroup(
                    name="Time-span settings",
                    description="Please define the time span. This action will check if current time is in defined time span.",
                    fields=[
                        FormField(
                            id="timezone",
                            name="Timezone",
                            description="Type time zone or path to time zone, eg. Europe/Paris, or session@context.time.tz",
                            component=FormComponent(type="dotPath", props={})
                        ),
                        FormField(
                            id="start",
                            name="Start time",
                            description="This is the beginning of time span. Start time must be before end time.",
                            component=FormComponent(type="text", props={
                                "label": "Start time"
                            })
                        ),
                        FormField(
                            id="end",
                            name="End time",
                            description="This is the end of time span. End time must be after start time.",
                            component=FormComponent(type="text", props={
                                "label": "End time"
                            })
                        ),
                    ]
                )
            ]
            ),
        ),
        metadata=MetaData(
            name='Is time between dates',
            desc='Checks if the current time is within defined time span.',
            icon='profiler',
            group=["Time"],
            tags=['condition'],
            type="condNode",
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "in": PortDoc(desc="Returns input payload if local time is in the defined range."),
                    "out": PortDoc(desc="Returns input payload if local time outside in the defined range."),
                }
            )
        )
    )
