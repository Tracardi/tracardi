from datetime import datetime
from typing import List

import pytz
from pydantic import field_validator, BaseModel
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class TodayConfiguration(BaseModel):
    timezone: str

    @field_validator('timezone')
    @classmethod
    def field_must_match(cls, value):
        if len(value) < 1:
            raise ValueError("Event type can not be empty.")

        if value != value.strip():
            raise ValueError(f"This field must not have space. Space is at the end or start of '{value}'")

        # if not re.match(
        #         r'^(payload|session|event|profile|flow|source|context)\@[a-zA-Z0-9\._\-]+$',
        #         value.strip()
        # ):
        #     raise ValueError("This field must be in form of dot notation. E.g. "
        #                      "session@context.time.tz")
        return value


def validate(config: dict) -> TodayConfiguration:
    return TodayConfiguration(**config)


class TodayAction(ActionRunner):

    week_days: List[str]
    config: TodayConfiguration

    async def set_up(self, init):
        self.config = validate(init)
        self.week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)

        try:
            if self.config.timezone is not None:
                time_zone = dot[self.config.timezone]
                time_zone = pytz.timezone(time_zone)
                local_time = datetime.now(time_zone)
                server_time = local_time.today()
            else:
                local_time = datetime.today()
                server_time = datetime.today()
        except KeyError as e:
            return Result(port="payload", value={"message": f"Unavailable time zone in current session. Details: {str(e)}"})

        return Result(port="payload", value={
            'utcTime': server_time.utcnow(),
            "timestamp": server_time.timestamp(),
            "server": {
                "dayOfWeek": self.week_days[server_time.weekday()],
                "day": server_time.day,
                "month": server_time.month,
                "year": server_time.year,
                "week": server_time.isoweekday(),
                "hour": server_time.hour,
                "minute": server_time.minute,
                "second": server_time.second,
                "ms": server_time.microsecond,
                "time": server_time.time(),
                "fold": server_time.fold,
                "iso": server_time.isoformat()
            },
            "local": {
                "dayOfWeek": self.week_days[local_time.weekday()],
                "day": local_time.day,
                "month": local_time.month,
                "year": local_time.year,
                "week": local_time.isoweekday(),
                "hour": local_time.hour,
                "minute": local_time.minute,
                "second": local_time.second,
                "ms": local_time.microsecond,
                "time": local_time.time(),
                "fold": local_time.fold,
                "iso": local_time.isoformat()
            }

        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.time.today_action',
            className='TodayAction',
            inputs=["payload"],
            outputs=["payload", "error"],
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={"timezone": "session@context.time.tz"},
            manual="today_action",
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="timezone",
                            name="Path to timezone",
                            description="Type path to field that has timezone. "
                                        "E.g. session@context.time.tz",
                            component=FormComponent(type="dotPath", props={"label": "Timezone"})
                        )
                    ]
                )
            ]),

        ),
        metadata=MetaData(
            name='Today',
            desc='Returns information about current time, month, day, etc. It will consists of day of the week, date and current time.',
            icon='today',
            group=["Time"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns payload containing current date, time, etc."),
                    "error": PortDoc(desc="This port returns error message.")
                }
            )
        )
    )
