from dotty_dict import dotty


def test_spaces():
    a = {
        "A": {"a b c": 1}
    }

    b = dotty(a)
    assert b["A.a b c"] == 1


def test_none_existent_value():
    a = {
        "A": None
    }
    a = dotty(a)
    assert not "A.c.d" in a
