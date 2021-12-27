import re


def validate_dot_path(dot_path: str) -> None:
    if not re.fullmatch(r"(payload|event|flow|profile|session)@[a-zA-Z0-9_.\-]*$", dot_path):
        raise ValueError(f"Given dot path is incorrect.")