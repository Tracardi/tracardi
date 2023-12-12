from datetime import datetime

from pydantic import field_validator, BaseModel, validator
from pytimeparse.timeparse import timeparse

from tracardi.service.utils.date import now_in_utc


class Schedule(BaseModel):
    type: str = "date|delta|interval"
    time: str = now_in_utc()

    @field_validator("type")
    @classmethod
    def _validate_type(cls, value):
        if value not in ("delta", "date", "interval"):
            raise ValueError("'type' field must contain 'date', 'delta' or 'interval'.")
        return value

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("time")
    def _validate_time(cls, value, values):
        if values["type"] in ("delta", "interval") and timeparse(value) is None:
            raise ValueError("value of 'time' is invalid according to type '{}'".format(values["type"]))
        else:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        return value

    def get_parsed_time(self):
        if self.type in ["interval", "delta"]:
            return timeparse(self.time)
        elif self.type == "date":
            return datetime.strptime(self.time, "%Y-%m-%dT%H:%M:%S.%f").timestamp()
