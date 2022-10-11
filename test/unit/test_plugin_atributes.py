import pytest

from tracardi.service.plugin.runner import ActionRunner


class A(ActionRunner):
    a: str


def test_should_not_mutate_attributes():
    a1 = A()
    a2 = A()

    a1.a = "abc"
    with pytest.raises(AttributeError):
        b = a2.a

    a2.a = "123"

    assert a1.a != a2.a


def test_should_mutate_class_attribute():
    a1 = A()
    a2 = A()

    A.a = "abc"
    assert a2.a == a1.a

