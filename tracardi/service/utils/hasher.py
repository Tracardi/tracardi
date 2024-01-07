from hashlib import md5

from tracardi.config import tracardi


def hash_id(value:str, prefix: str) -> str:
    if tracardi.hash_id_webhook is None:
        raise ValueError("Env HASH_ID_WEBHOOK is not set.")
    hash = md5(f"{tracardi.hash_id_webhook}-{value}".encode()).hexdigest()
    return f"{prefix[0:3]}-{hash[0:8]}-{hash[8:12]}-{hash[12:16]}-{hash[16:20]}-{hash[20:32]}"