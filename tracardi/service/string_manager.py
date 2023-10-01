from typing import Optional


def capitalize_event_type_id(event_type_id: Optional[str]) -> str:
    if not event_type_id:
        return ""
    words = [word.capitalize() for word in event_type_id.split('-')]
    return " ".join(words)


