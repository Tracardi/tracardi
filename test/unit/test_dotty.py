from dotty_dict import dotty


def test_none_to_dotty():
    a = dotty(None)
    assert bool(a) is False

def test_list_in_dotty():
    a = dotty({"id":"a", "ids": ["a"]})
    a['ids'].append("b")
    assert len(a['ids']) == 2
    assert a.to_dict()['ids'] == a['ids']


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


def test_sub_field_is_not_dotty():
    a = {
        "A": {
            "B": {
                "C": {
                    "D": 1
                }
            }
        }
    }
    a = dotty(a)
    b = a['A.B']
    assert isinstance(b, dict)


def test_get_data():
    a = {
        "A": {
            "B": {
                "C": {
                    "D": 1
                }
            }
        }
    }
    a = dotty(a)
    b = a.get('A.B')
    assert isinstance(b, dict)
    d = a.get('A.B.C.D')
    assert d == 1
    n = a.get('A.B.C.N', "default")
    assert n == 'default'



def test_if_dict_assigned_can_be_accessed():
    a = {
        "A": {
            "B": 1
        }
    }
    a = dotty(a)

    # Simple dict
    a['A.B'] = {
        "C": {
            "D": 1
        }
    }
    assert a['A.B.C.D'] == 1

    a = {
        "A": {
            "B": 1
        }
    }
    a = dotty(a)

    # Dotty
    a['A.B'] = dotty({
        "C": {
            "D": 1
        }
    })
    assert a['A.B.C.D'] == 1
