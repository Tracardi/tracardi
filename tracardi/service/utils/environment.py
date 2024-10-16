import os


def get_env_as_int(env_key, default_value):
    value = os.environ.get(env_key, default_value)
    if not value:
        return default_value
    try:
        return int(value)
    except Exception:
        return default_value


def _str_to_bool(value):
    if isinstance(value, bool):
        return value

    true_values = ['yes', 'on', 'true']
    false_values = ['no', 'off', 'false']
    value_lower = value.lower()
    if value_lower in true_values:
        return True
    elif value_lower in false_values:
        return False
    else:
        raise ValueError(f"Invalid value for boolean setting: {value}")


def get_env_as_bool(env_key, default_value) -> bool:
    value = os.environ.get(env_key, default_value)
    return _str_to_bool(value)
