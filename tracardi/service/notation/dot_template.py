import re

from .dot_accessor import DotAccessor
from ..singleton import Singleton


class DotTemplate(metaclass=Singleton):

    def __init__(self):
        # Updated regex to capture optional format strings and "no data" strings
        self._regex = re.compile(r"\{{2}\s*((?:payload|profile|event|session|flow|memory)"
                                 r"@[\[\]0-9a-zA-Z_\-\.]+(?<![\.\[]))"
                                 r"(?:\s*\?\s*\"([^\"]+)\")?"
                                 r"(?:\s*!\s*\"([^\"]+)\")?\s*\}{2}")

    def render(self, template, dot: DotAccessor):
        def replacement(match):
            key = match.group(1)
            format_string = match.group(2)
            no_data_string = match.group(3)

            # Try to get the value using the dot accessor. If not found, use no_data_string if available, else 'unknown'
            try:
                value = dot[key]
                if value is None:
                    raise KeyError  # Treat None as missing data for this purpose
            except KeyError:
                return no_data_string if no_data_string is not None else "unknown"

            # If a format string is provided, format the value with it. Otherwise, just return the value
            if format_string:
                return format_string % value
            else:
                return str(value)

        return re.sub(self._regex, replacement, template)
