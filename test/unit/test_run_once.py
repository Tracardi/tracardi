from tracardi.common.decorator.run_once import run_once


# Example functions to test
@run_once
def add(x, y):
    return x + y


@run_once
def multiply(x, y):
    return x * y


@run_once
def say_hello(name):
    return f"Hello, {name}!"


# Tests
def test_basic_functionality():
    assert add(1, 2) == 3
    assert add(1, 2) == 3  # Should not re-execute the function
    assert multiply(2, 3) == 6
    assert multiply(2, 3) == 6  # Should not re-execute the function


def test_different_functions_with_same_args():
    assert add(1, 2) == 3
    assert multiply(1, 2) == 2  # Different function, so different result


def test_different_args():
    assert add(1, 2) == 3
    assert add(2, 3) == 5  # Different arguments should allow re-execution
    assert multiply(2, 3) == 6
    assert multiply(3, 4) == 12  # Different arguments should allow re-execution


def test_kwargs_handling():
    @run_once
    def greet(greeting, name="World"):
        return f"{greeting}, {name}!"

    assert greet("Hi") == "Hi, World!"
    assert greet("Hi", name="World") == "Hi, World!"
    assert greet("Hello", name="Alice") == "Hello, Alice!"
    assert greet("Hello", name="Alice") == "Hello, Alice!"  # Cached


def test_non_colliding_cache():
    assert add(1, 2) == 3
    assert multiply(1, 2) == 2  # Should not collide with `add`


def test_same_function_different_args():
    @run_once
    def pow(x, y):
        return x ** y

    assert pow(2, 3) == 8
    assert pow(3, 2) == 9
    assert pow(2, 3) == 8  # Cached


def test_cache_persistence():
    # Ensure cache persists across multiple calls
    assert add(1, 2) == 3
    assert add(1, 2) == 3  # Should return cached result
    assert multiply(1, 2) == 2
    assert multiply(1, 2) == 2  # Should return cached result


def test_function_identity():
    # Ensure `run_once` works with different functions
    @run_once
    def a(x):
        return x + 10

    @run_once
    def b(x):
        return x * 2

    assert a(1) == 11
    assert b(1) == 2
    assert a(1) == 11  # Cached
    assert b(1) == 2  # Cached


def test_function_runs_once():
    counter = {"count": 0}

    @run_once
    def increment():
        counter["count"] += 1
        return counter["count"]

    # Call the function multiple times
    assert increment() == 1  # First call runs the function
    assert increment() == 1  # Subsequent calls should return the cached result
    assert increment() == 1  # Cached result persists

    # Ensure the function was executed only once
    assert counter["count"] == 1
