from dotty_dict import dotty


def test_spaces():
    a = {
        "A": {"a b c": 1}
    }

    b = dotty(a)
    assert b["A.a b c"] == 1
