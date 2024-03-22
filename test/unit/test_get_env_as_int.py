import os

from tracardi.service.utils.environment import get_env_as_int


def test_returns_integer_value():
    os.environ["ENV_VAR"] = "123"
    assert get_env_as_int("ENV_VAR", 0) == 123


def test_returns_zero():
    os.environ.pop("ENV_VAR", None)
    assert get_env_as_int("ENV_VAR", 1234) == 1234


def test_returns_none():
    assert get_env_as_int("NONE", 356) == 356
