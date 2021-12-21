from typing import Optional

from pydantic import BaseModel, validator
from dateutil.parser import ParserError, parse
import re


class Config(BaseModel):
    reference_date: str
    now_format: str
    now: str

    @validator("now_format")
    def validate_format(cls, value):
        if value not in ("now", "date", "path"):
            raise ValueError("'now_format' must be either 'now', 'date' or 'path'.")
        return value

    @validator("now")
    def validate_now(cls, value, values):
        if values["now_format"] == "now" and value != "now":
            raise ValueError(f"Given value ({value}) is incorrect for format Now. Correct value is just now.")
        elif values["now_format"] == "date":
            try:
                parse(value)
            except ParserError:
                raise ValueError(f"Given date is invalid in terms of format or value.")
        elif values["now_format"] == "path":
            if not re.fullmatch(r"(payload|event|flow|profile|session)@[a-zA-Z0-9_.\-]*$", value):
                raise ValueError(f"Given dot path is incorrect.")
        return value
