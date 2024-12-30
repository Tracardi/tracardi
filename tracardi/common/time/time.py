from datetime import datetime
from typing import Optional

from dateutil.parser import parse
from pytimeparse import parse as parse_delta


def parse_date(string, fuzzy=False) -> Optional[datetime]:
    try:
        return parse(string, fuzzy=fuzzy)

    except ValueError:
        return None


def parse_date_delta(string) -> Optional[int]:
    return parse_delta(string)
