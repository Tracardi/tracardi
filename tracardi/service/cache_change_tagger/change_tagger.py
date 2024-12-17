from functools import wraps
from time import time

from tracardi.service.adapter.cache_adaper_selector import cache_adapter

_cache = cache_adapter()


def _get_key(database: str, table: str):
    return f"db:{database}:table:{table}:change"


def table_cache_updated(database: str, table: str):
    _cache.delete(_get_key(database, table))


def on_table_change(database: str, table: str):
    """
    Decorator to call table_changed after successful execution of the decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)  # Execute the function
                _cache.set(_get_key(database, table), time())  # Call table_changed on success
                return result
            except Exception as e:
                raise e  # Re-raise exception

        return wrapper

    return decorator

# # Example usage:
#
# @on_table_change(database="my_db", table="my_table")
# def my_function():
#     print("Executing my_function...")
#     # Simulating some logic
#     return "Success!"
#
#
# # Test the decorators
# if __name__ == "__main__":
#     with ServerContext(Context(production=False)):
#         print(my_function())  # Should execute successfully and trigger table_changed
