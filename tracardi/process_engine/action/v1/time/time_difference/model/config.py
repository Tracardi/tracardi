from pydantic import BaseModel, validator
from dateutil.parser import ParserError, parse
import re


class Config(BaseModel):
    reference_date: str
    now_format: str
    now: str

    @validator("reference_date")
    def validate_reference(cls, v):
        if not re.fullmatch(r"(payload|event|flow|profile|session)@[a-zA-Z0-9_.\-]*$", v):
            raise ValueError(f"Given dot path is incorrect.")
        return v

    @validator("now_format")
    def validate_format(cls, v):
        if v not in ("now", "date", "path"):
            raise ValueError("'now_format' must be either 'now', 'date' or 'path'.")
        return v

    @validator("now")
    def validate_now(cls, v, values):
        if values["now_format"] == "now" and v != "now":
            raise ValueError(f"Given value ({v}) is incorrect for format Now. Correct value is just now.")
        elif values["now_format"] == "date":
            try:
                parse(v)
            except ParserError:
                raise ValueError(f"Given date is invalid in terms of format or value.")
        elif values["now_format"] == "path":
            if not re.fullmatch(r"(payload|event|flow|profile|session)@[a-zA-Z0-9_.\-]*$", v):
                raise ValueError(f"Given dot path is incorrect.")
        return v
