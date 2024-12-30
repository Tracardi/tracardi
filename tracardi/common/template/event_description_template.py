import re

from tracardi.common.singleton import Singleton


class EventDescriptionTemplate(metaclass=Singleton):

    def __init__(self):
        # Updated regex to optionally capture the "render if no value" string after an "!"
        self._regex = re.compile(r'(\{\{\s*([^\?]+?)(?:\s*\?\s*"([^"]+)")?(?:\s*!\s*"([^"]+)")?\s*\}\})')

    @staticmethod
    def _replace_with_computed_text(match, flat_event):
        field_name = match.group(2).strip()

        # Determine if a default value is specified after "!"
        default_value = match.group(4).strip() if match.group(4) else "unknown"

        # Check if there's a format string
        if match.group(3):
            format_string = match.group(3).strip()
            # Try to fetch the field value; use format_string with field_name or default_value
            field_value = flat_event.get(field_name, None)
            if field_value is not None:
                replacement_text = format_string.replace("%s", str(field_value))
            else:
                replacement_text = default_value
        else:
            # If no format string is provided, directly use the field value or the default_value
            replacement_text = str(flat_event.get(field_name, default_value))

        return replacement_text

    def render(self, template, flat_event):
        return re.sub(self._regex, lambda x: self._replace_with_computed_text(x, flat_event), template)
