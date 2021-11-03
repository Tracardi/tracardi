from typing import Any

from pydantic import BaseModel
from tracardi.domain.enum.yes_no import YesNo


class Settings(BaseModel):
    enabled: bool = True
    hidden: bool = False

    @staticmethod
    def as_bool(state: YesNo):
        return state.value == state.yes


class SystemSettings(BaseModel):
    label: str
    value: Any
    desc: str
