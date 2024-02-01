import re


def validate_email(value) -> bool:
    if re.fullmatch(r'([A-Za-z0-9]+[.\-_+])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', value):
        return True
    return False
