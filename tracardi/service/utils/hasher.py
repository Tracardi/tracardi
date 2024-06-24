from datetime import datetime

from hashlib import md5
import json
from tracardi.config import tracardi


def uuid4_from_md5(hash: str):
    return f"{hash[0:8]}-{hash[8:12]}-{hash[12:16]}-{hash[16:20]}-{hash[20:32]}"


def hash_pk_guid(value: str, prefix: str):
    if not tracardi.is_apm_on():
        raise ValueError("Env AUTO_PROFILE_MERGING is not set.")

    hash = md5(f"{tracardi.auto_profile_merging}-{value}".encode()).hexdigest()
    pk_guid = uuid4_from_md5(hash)[:24]

    return f"{prefix[0:3]}-{pk_guid}"


def get_pk_timestamp() -> str:
    # Calculate the days and seconds since 2014-01-01
    start_date = datetime(2024, 1, 1)
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)  # Start of the current day
    delta_days = today_start - start_date  # Full days since start_date
    days = delta_days.days
    seconds_today = (now - today_start).seconds  # Seconds passed today since midnight

    # Format days and seconds to be exactly 5 characters long
    days_str = str(days).zfill(5)
    seconds_str = str(seconds_today).zfill(5)

    return days_str + seconds_str


def timestamped_hash_id(value: str, prefix: str, pk_guid: str = None) -> str:
    if pk_guid is None:
        pk_guid = hash_pk_guid(value, prefix)
    pk_timestamp = get_pk_timestamp()

    return pk_guid + pk_timestamp


def has_hash_id(hash_id: str, ids) -> bool:
    return hash_id in ids


def hash_id(value: str, prefix: str):
    if not tracardi.is_apm_on():
        raise ValueError("Env AUTO_PROFILE_MERGING is not set.")

    hash = md5(f"{tracardi.auto_profile_merging}-{value}".encode()).hexdigest()
    pk_guid = uuid4_from_md5(hash)

    return f"{prefix[0:3]}-{pk_guid}"


def has_pk_guid(pk_guid, ids):
    for string in ids:
        if string.startswith(pk_guid):
            return True
    return False


def deep_sort(obj):
    """
    Recursively sort any lists it finds (and convert dictionaries to lists of (key, value) pairs so they can be sorted).
    """
    if isinstance(obj, dict):
        return sorted((k, deep_sort(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(deep_sort(x) for x in obj)
    else:
        return obj


def hash_deep_dict(d):
    # Recursively sort the dictionary and convert it into a JSON string
    sorted_dict = deep_sort(d)
    serialized_dict = json.dumps(sorted_dict)
    # Hash the serialized string
    dict_hash = md5(serialized_dict.encode()).hexdigest()
    return dict_hash
