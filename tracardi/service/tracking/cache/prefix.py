from tracardi.service.utils.validators import is_valid_hex


def get_cache_prefix(string: str) -> str:
    if len(string) == 1:
        prefix = f"0{string}"
    else:
        prefix = string
    if is_valid_hex(prefix):
        return prefix
    return '00'
