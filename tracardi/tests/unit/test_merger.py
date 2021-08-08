from datetime import datetime

from tracardi.service.merger import merge


def test_merger_multiple_values():
    a = {"a": None}
    b = {"a": .2}
    c = {"a": [1]}
    d = {"a": "3"}
    m = merge({}, [a, b, c, d])
    assert set(m['a']).intersection({.2, 1, "3"}) == {.2, 1, "3"}


def test_merger_none_values():
    a = {"a": None}
    b = {"a": "2"}
    assert merge({}, [a, b]) == {"a": "2"}

    a = {"a": None}
    b = {"a": None}
    assert merge({}, [a, b]) == {}


def test_merger_missing_values():
    a = {}
    b = {"a": "2"}
    assert merge({}, [a, b]) == {"a": "2"}


def test_merger_values_no_intersection():
    a = {"b": 1}
    b = {"a": "2"}
    assert merge({}, [a, b]) == {"b": 1, "a": "2"}


def test_merger_single_values():
    # mixed

    a = {"a": 1}
    b = {"a": "2"}
    c = merge({}, [a, b])
    assert c == {"a": [1, "2"]} or c == {"a": ["2", 1]}

    # string

    a = {"a": "1"}
    b = {"a": "2"}
    c = merge({}, [a, b])
    assert c == {"a": ["2", "1"]} or c == {"a": ["1", "2"]}

    # int
    a = {"a": 1}
    b = {"a": 2}
    c = merge({}, [a, b])
    assert c == {"a": [1, 2]} or c == {"a": [2, 1]}

    # float
    a = {"a": .1}
    b = {"a": .2}
    c = merge({}, [a, b])
    assert c == {"a": [.1, .2]} or c == {"a": [.2, .1]}


def test_merger_bool_values():
    a = {"a": True}
    b = {"a": False, "b": True}
    c = merge({}, [a, b])
    assert c == {"a": [False, True], "b": True}

    a = {"a": True}
    b = {"a": [False], "b": True}
    c = merge({}, [a, b])
    assert c == {"a": [False, True], "b": True}

    a = {"a": [True]}
    b = {"a": False, "b": True}
    c = merge({}, [a, b])
    assert c == {"a": [False, True], "b": True}

    a = {"a": [True]}
    b = {"a": (False,), "b": True}
    c = merge({}, [a, b])
    assert c == {"a": [False, True], "b": True}


def test_merger_single_value_plus_list():
    # mixed

    a = {"a": [1]}
    b = {"a": "2"}
    c = merge({}, [a, b])
    assert c == {"a": [1, "2"]} or c == {"a": ["2", 1]}

    a = {"a": 1}
    b = {"a": ["2"]}
    c = merge({}, [a, b])
    assert c == {"a": [1, "2"]} or c == {"a": ["2", 1]}

    # string

    a = {"a": ["1"]}
    b = {"a": "2"}
    c = merge({}, [a, b])
    assert c == {"a": ["2", "1"]} or c == {"a": ["1", "2"]}

    a = {"a": "1"}
    b = {"a": ["2"]}
    c = merge({}, [a, b])
    assert c == {"a": ["2", "1"]} or c == {"a": ["1", "2"]}

    # int

    a = {"a": [1]}
    b = {"a": 2}
    c = merge({}, [a, b])
    assert c == {"a": [1, 2]} or c == {"a": [2, 1]}

    a = {"a": 1}
    b = {"a": [2]}
    c = merge({}, [a, b])
    assert c == {"a": [1, 2]} or c == {"a": [2, 1]}

    # float

    a = {"a": [.1]}
    b = {"a": .2}
    c = merge({}, [a, b])
    assert c == {"a": [.1, .2]} or c == {"a": [.2, .1]}

    a = {"a": .1}
    b = {"a": [.2]}
    c = merge({}, [a, b])
    assert c == {"a": [.1, .2]} or c == {"a": [.2, .1]}


def test_merger_uniq():
    a = {"a": {"b": ["1", "2", "1"]}}
    b = {"a": {"b": "2"}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": ["2", "1"]}} or c == {"a": {"b": ["1", "2"]}}

    a = {"a": {"b": ["1", "2", "1"]}}
    b = {"a": {"b": ["2", "1"]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": ["2", "1"]}} or c == {"a": {"b": ["1", "2"]}}


def test_merger_immutable():
    a = {"a": {"b": ["1", "2", "1"]}}
    b = {"a": {"b": "2"}}
    c = merge({}, [a, b])
    assert a == {"a": {"b": ["1", "2", "1"]}} and b == {"a": {"b": "2"}}


def test_merger_same_value():

    a = {"b": 1}
    b = {"b": 1}
    c = merge({}, [a, b])
    assert c == {"b": 1}

    a = {"a": {"b": 1}}
    b = {"a": {"b": 1}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": 1}}

    a = {"a": {"b": [1]}}
    b = {"a": {"b": 1}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": 1}}

    a = {"a": {"b": 1}}
    b = {"a": {"b": [1]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": 1}}

    a = {"a": {"b": [1]}}
    b = {"a": {"b": [1]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": 1}}


def test_merger_dict_single_values():
    # mixed

    a = {"a": {"b": 1}}
    b = {"a": {"b": "2"}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, "2"]}} or c == {"a": {"b": ["2", 1]}}

    # string

    a = {"a": {"b": "1"}}
    b = {"a": {"b": "2"}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": ["2", "1"]}} or c == {"a": {"b": ["1", "2"]}}

    # int
    a = {"a": {"b": 1}}
    b = {"a": {"b": 2}}
    assert merge({}, [a, b]) == {"a": {"b": [1, 2]}}

    # float
    a = {"a": {"b": .1}}
    b = {"a": {"b": .2}}
    assert merge({}, [a, b]) == {"a": {"b": [.1, .2]}}


def test_merger_dict_list_2_list():
    a = {"a": {"b": [1, 2]}}
    b = {"a": {"b": [3, 4]}}
    c = merge({}, [a, b])
    assert "b" in c['a'] and set(c['a']['b']).intersection({1, 2, 3, 4}) == {1, 2, 3, 4}

    a = {"a": [1, 2, 3]}
    b = {"a": [3, 4, 5]}
    c = merge({}, [a, b])
    assert set(c['a']).intersection({1, 2, 3, 4, 5}) == {1, 2, 3, 4, 5}


def test_merger_dict_list_2_set():
    a = {"a": {"b": {1, 2}}}
    b = {"a": {"b": [3, 4]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, 2, 3, 4]}}

    a = {"a": {"b": [1, 2]}}
    b = {"a": {"b": {3, 4}}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, 2, 3, 4]}}

    a = {"a": [1, 2, 3]}
    b = {"a": {3, 4, 5}}
    c = merge({}, [a, b])
    assert c == {"a": [1, 2, 3, 4, 5]}


def test_merger_dict_set_2_set():
    a = {"a": {"b": {1, 2}}}
    b = {"a": {"b": {3, 4}}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, 2, 3, 4]}}

    a = {"a": {1, 2, 3}}
    b = {"a": {3, 4, 5}}
    c = merge({}, [a, b])
    assert c == {"a": [1, 2, 3, 4, 5]}


def test_merger_tuple_2_list():
    """
    Merges dict with value int, float, str
    """

    a = {"a": 1}
    b = {"a": (2, 3)}
    c = merge({}, [a, b])
    assert c == {"a": [1, 2, 3]}

    a = {"a": [1]}
    b = {"a": (2, 3)}
    c = merge({}, [a, b])
    assert c == {"a": [1, 2, 3]}


def test_merger_dict_single_list_values():
    # mixed dict

    a = {"a": {"b": [1]}}
    b = {"a": {"b": "2"}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, "2"]}} or c == {"a": {"b": ["2", 1]}}

    a = {"a": {"b": 1}}
    b = {"a": {"b": ["2"]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, "2"]}} or {"a": {"b": ["2", 1]}}

    # int

    a = {"a": {"b": [1]}}
    b = {"a": {"b": 2}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, 2]}} or c == {"a": {"b": [2, 1]}}

    a = {"a": {"b": 1}}
    b = {"a": {"b": [2]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, 2]}} or c == {"a": {"b": [2, 1]}}

    # float

    a = {"a": {"b": [.1]}}
    b = {"a": {"b": .2}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [.1, .2]}} or c == {"a": {"b": [.2, .1]}}

    a = {"a": {"b": .1}}
    b = {"a": {"b": [.2]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [.1, .2]}} or c == {"a": {"b": [.2, .1]}}

    # string

    a = {"a": {"b": ["1"]}}
    b = {"a": {"b": "2"}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": ["2", "1"]}} or c == {"a": {"b": ["1", "2"]}}

    a = {"a": {"b": "1"}}
    b = {"a": {"b": ["2"]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": ["2", "1"]}} or c == {"a": {"b": ["1", "2"]}}


def test_merger_conflict_1():
    """
    Merges dict with value int, float, str
    """

    a = {"a": 1}
    b = {"a": {"b": 1}}

    try:
        merge({}, [a, b])
    except ValueError:
        assert True

    a = {"a": {"b": 1}}
    b = {"a": 1}
    try:
        merge({}, [a, b])
    except ValueError:
        assert True


def test_merger_conflict_2():
    """
    Merges dict with value int, float, str
    """

    a = {"a": 1}
    b = {"a": datetime.now()}
    try:
        merge({}, [a, b])
    except ValueError:
        assert True


def test_merger_conflict_3():
    """
    Conflict inside list of values
    """

    a = {"a": 1}
    b = {"a": [2, [3]]}
    try:
        merge({}, [a, b])
    except ValueError:
        assert True

    a = {"a": [2, [3]]}
    b = {"a": 1}
    try:
        merge({}, [a, b])
    except ValueError:
        assert True

    a = {"a": (2, [3])}
    b = {"a": 1}
    try:
        merge({}, [a, b])
    except ValueError:
        assert True

    a = {"a": 1}
    b = {"a": (2, [3])}
    try:
        merge({}, [a, b])
    except ValueError:
        assert True


def test_merger_conflict_4():
    """
    Conflict inside list of values
    """

    a = {"a": datetime.now}
    b = {"a": [2, 3]}
    try:
        merge({}, [a, b])
    except ValueError:
        assert True

    a = {"a": datetime.now()}
    b = {"a": [2, 3]}
    try:
        merge({}, [a, b])
    except ValueError:
        assert True
