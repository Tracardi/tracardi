def run_once(func):
    result = None

    def wrapper(*args, **kwargs):
        nonlocal result
        if result is None:
            result = func(*args, **kwargs)
        return result

    return wrapper
