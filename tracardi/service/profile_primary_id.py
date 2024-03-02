from tracardi.domain.profile_data import PREFIX_IDENTIFIER_PK, PREFIX_IDENTIFIER_ID, PREFIX_EMAIL_MAIN, \
    PREFIX_PHONE_MAIN

from typing import Optional, List
from ..exceptions.log_handler import get_logger

logger = get_logger(__name__)


def sort_strings_by_prefix_priority(strings: List[str], prefixes: tuple):
    """
    Sorts the strings by the priority of their prefixes.

    :param strings: The list of strings to sort.
    :param prefixes: A tuple or list of prefixes in priority order.
    :return: A list of strings sorted by prefix priority.
    """
    prefix_priority = {prefix: i for i, prefix in enumerate(prefixes)}

    def get_priority(string):
        for prefix in prefixes:
            if string.startswith(prefix):
                return prefix_priority[prefix]
        return len(prefixes)  # Assign a lower priority if no prefix matches

    return sorted(strings, key=get_priority)


def find_first_prefixed_string(sorted_strings: List[str], prefixes: tuple) -> Optional[str]:
    """
    Finds the first string in a sorted list that starts with one of the prefixes.

    :param sorted_strings: The list of strings sorted by prefix priority.
    :param prefixes: The list of prefixes.
    :return: The first matching string or None if no match is found.
    """
    for string in sorted_strings:
        if any(string.startswith(prefix) for prefix in prefixes):
            return string
    return None



def get_profile_primary_id(profile) -> str:
    # These are the priorities for the Primary Key selection
    priorities = (PREFIX_IDENTIFIER_PK, PREFIX_IDENTIFIER_ID, PREFIX_EMAIL_MAIN, PREFIX_PHONE_MAIN)
    _sorted_ids = sort_strings_by_prefix_priority(profile.ids, priorities)
    primary_id = find_first_prefixed_string(_sorted_ids, priorities)
    if primary_id:
        return primary_id
    return profile.id