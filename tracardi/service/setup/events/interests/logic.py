import logging

from dotty_dict import Dotty

from tracardi.config import tracardi
from tracardi.domain.profile import FlatProfile
from tracardi.exceptions.log_handler import log_handler




def _get_interest_and_value(event: Dotty):
    interest, value = None, None
    if 'properties.interest' in event:
        interest = event['properties.interest']
        if 'properties.value' in event:
            value = float(event['properties.value'])
        else:
            value = 1.0

    return interest, value

def increase_interest(event: Dotty, profile: FlatProfile):
    interest, value = _get_interest_and_value(event)
    if isinstance(interest, str):
        profile.increase_interest(interest, value)

def decrease_interest(event: Dotty, profile: FlatProfile):
    interest, value = _get_interest_and_value(event)
    if isinstance(interest, str):
        profile.decrease_interest(interest, value)

def reset_interest(event: Dotty, profile: FlatProfile):
    interest, value = _get_interest_and_value(event)
    if isinstance(interest, str):
        profile.reset_interest(interest, value)