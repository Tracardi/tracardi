from tracardi.service.singleton import Singleton


def test_singleton():
    class Single(metaclass=Singleton):

        def __init__(self):
            self.prop = 1

    x = Single()
    y = Single()

    x.prop = 2
    assert y.prop == 2
    assert y == x
