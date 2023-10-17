import os


def get_env_as_int(env_key, default_value):
    value = os.environ.get(env_key, default_value)
    if not value:
        return default_value
    return int(value)
