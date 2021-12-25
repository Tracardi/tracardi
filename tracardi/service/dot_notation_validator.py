import re


def is_dot_notation_valid(value: str) -> bool:
    return re.fullmatch(r"(payload|event|flow|profile|session)@[a-zA-Z0-9_.\-]*$", value) is not None
