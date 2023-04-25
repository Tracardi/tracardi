def capitalize_event_type_id(event_type_id) -> str:
    words = [word.capitalize() for word in event_type_id.split('-')]
    return " ".join(words)
