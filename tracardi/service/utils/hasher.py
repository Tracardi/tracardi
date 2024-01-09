from hashlib import md5

from tracardi.config import tracardi


def hash_id(value:str, prefix: str) -> str:
    if tracardi.auto_profile_merging is None:
        raise ValueError("Env AUTO_PROFILE_MERGING is not set.")
    hash = md5(f"{tracardi.auto_profile_merging}-{value}".encode()).hexdigest()
    return f"{prefix[0:3]}-{hash[0:8]}-{hash[8:12]}-{hash[12:16]}-{hash[16:20]}-{hash[20:32]}"