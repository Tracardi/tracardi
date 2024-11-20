def run_once(func):
    cache = {}

    def wrapper(*args, **kwargs):
        key = (func, args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper
