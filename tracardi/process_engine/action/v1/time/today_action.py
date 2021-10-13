import re
from datetime import datetime

import pytz
from pydantic import BaseModel, validator
from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class TodayConfiguration(BaseModel):
    timezone: str

    @validator('timezone')
    def field_must_match(cls, value):
        if len(value) < 1:
            raise ValueError("Event type can not be empty.")

        if value != value.strip():
            raise ValueError(f"This field must not have space. Space is at the end or start of '{value}'")

        if not re.match(
                r'^(payload|session|event|profile|flow|source|context)\@[a-zA-Z0-9\._\-]+$',
                value.strip()
        ):
            raise ValueError("This field must be in form of dot notation. E.g. "
                             "session@context.time.tz")
        return value


def validate(config: dict) -> TodayConfiguration:
    return TodayConfiguration(**config)


class TodayAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)
        self.week_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    async def run(self, payload):
        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)

        if self.config.timezone is not None:
            time_zone = dot[self.config.timezone]
            time_zone = pytz.timezone(time_zone)
            today = datetime.now(time_zone).today()
        else:
            today = datetime.today()

        return Result(port="payload", value={
            'utcTime': today.utcnow(),
            "dayOfWeek": self.week_days[today.weekday()],
            "day": today.day,
            "month": today.month,
            "year": today.year,
            "week": today.isoweekday(),
            "hour": today.hour,
            "minute": today.minute,
            "second": today.second,
            "ms": today.microsecond,
            "time": today.time(),
            "timestamp": today.timestamp(),
            "fold": today.fold,
            "iso": today.isoformat()
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.time.today_action',
            className='TodayAction',
            inputs=["payload"],
            outputs=["payload"],
            version='0.1.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={"timezone": "session@context.time.tz"},
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="timezone",
                            name="Path to timezone",
                            description="Provide path to field that has timezone. "
                                        "E.g. session@context.time.tz",
                            component=FormComponent(type="dotPath", props={"label": "Timezone"})
                        )
                    ]
                )
            ]),

        ),
        metadata=MetaData(
            name='Today',
            desc='Gets today object, that consists day of week, date and current time.',
            type='flowNode',
            width=100,
            height=100,
            icon='today',
            group=["Time"]
        )
    )
