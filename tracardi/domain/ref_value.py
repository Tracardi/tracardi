from typing import Any, Optional

from dotty_dict import dotty, Dotty
from pydantic import BaseModel

from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


class RefValue(BaseModel):
    value: Optional[str] = ''
    ref: bool

    def has_value(self) -> bool:
        return bool(self.value and self.value.strip())

    def get_value(self, payload: Any):
        value = None
        if self.has_value():
            if not self.ref:
                # Set plain value
                value = self.value.strip()
            else:
                # It is a reference to the event type in payload
                if isinstance(payload, Dotty):
                    dot = payload
                elif isinstance(payload, dict):
                    dot = dotty(payload)
                else:
                    raise ValueError(
                        f"Could not read value from {type(payload)}. Values can be read from dict or Dotty.")
                try:
                    value = dot[self.value.strip()]
                except KeyError:
                    logger.warning(f"Could not find value in payload at `{self.value}`. "
                                   f"Default value was returned.")

        return value
