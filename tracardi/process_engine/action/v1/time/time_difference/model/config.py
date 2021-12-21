from pydantic import BaseModel, validator
from dateutil.parser import ParserError, parse
from tracardi.service.dot_path_validator import validate_dot_path


class Config(BaseModel):
    reference_date_format: str
    reference_date: str
    now_format: str
    now: str

    @validator("reference_date_format")
    def validate_reference_date_format(cls, value):
        if value not in ("now", "date", "path"):
            raise ValueError("'reference_date_format' must be either 'now', 'date' or 'path'")
        return value

    @validator("reference_date")
    def validate_reference_date(cls, value, values):
        if values["reference_date_format"] == "now" and value != "now":
            raise ValueError(f"Given value ({value}) is incorrect for format Now. Correct value is just now.")
        elif values["reference_date_format"] == "date":
            try:
                parse(value)
            except ParserError:
                raise ValueError(f"Given date is invalid in terms of format or value.")
        elif values["reference_date_format"] == "path":
            validate_dot_path(value)
        return value

    @validator("now_format")
    def validate_now_format(cls, value):
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
            validate_dot_path(value)
        return value

