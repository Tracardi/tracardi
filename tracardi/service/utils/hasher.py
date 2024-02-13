from hashlib import md5
import json
from tracardi.config import tracardi


def uuid4_from_md5(hash: str):
    return f"{hash[0:8]}-{hash[8:12]}-{hash[12:16]}-{hash[16:20]}-{hash[20:32]}"


def hash_id(value: str, prefix: str) -> str:
    if not tracardi.is_apm_on():
        raise ValueError("Env AUTO_PROFILE_MERGING is not set.")
    hash = md5(f"{tracardi.auto_profile_merging}-{value}".encode()).hexdigest()
    return f"{prefix[0:3]}-{uuid4_from_md5(hash)}"


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
