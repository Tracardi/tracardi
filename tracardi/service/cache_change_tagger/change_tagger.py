from contextlib import contextmanager

from time import time

from tracardi.service.adapter.cache_adaper_selector import cache_adapter

_cache = cache_adapter()


def _get_key(database: str, table: str):
    return f"db:{database}.{table}:change"


@contextmanager
def invalidate_cache_on_update(database: str, table: str):
    try:
        yield  # Execute the function
        print(_get_key(database, table))
        _cache.delete(_get_key(database, table))
    except Exception as e:
        raise e  # Re-raise exception


@contextmanager
def validate_cache_on_load(database: str, table: str):
    try:
        yield  # Execute the function
        _cache.set(_get_key(database, table), time())  # Call table_changed on success

    except Exception as e:
        raise e  # Re-raise exception
