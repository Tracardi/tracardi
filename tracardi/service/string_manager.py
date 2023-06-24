import re
from typing import Optional

pattern = re.compile(r'[^a-z]')


def capitalize_event_type_id(event_type_id: Optional[str]) -> str:
    if not event_type_id:
        return ""
    words = [word.capitalize() for word in event_type_id.split('-')]
    return " ".join(words)


def remove_non_alpha(text):
    # Use regular expression to match only lowercase letters
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text
