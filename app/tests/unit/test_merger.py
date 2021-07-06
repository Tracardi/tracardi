from app.process_engine.action.v1.operations.merger import merge


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


def test_merger_single_value_plus_list():
    # mixed

    a = {"a": [1]}
    b = {"a": "2"}
    assert merge({}, [a, b]) == {"a": [1, "2"]}

    a = {"a": 1}
    b = {"a": ["2"]}
    assert merge({}, [a, b]) == {"a": [1, "2"]}

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
    assert c == {"a": [1, 2]}

    a = {"a": 1}
    b = {"a": [2]}
    c = merge({}, [a, b])
    assert c == {"a": [1, 2]}

    # float

    a = {"a": [.1]}
    b = {"a": .2}
    assert merge({}, [a, b]) == {"a": [.1, .2]}

    a = {"a": .1}
    b = {"a": [.2]}
    assert merge({}, [a, b]) == {"a": [.1, .2]}


def test_merger_uniq():
    a = {"a": {"b": ["1", "2", "1"]}}
    b = {"a": {"b": "2"}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": ["2", "1"]}} or c == {"a": {"b": ["1", "2"]}}

    a = {"a": {"b": ["1", "2", "1"]}}
    b = {"a": {"b": ["2", "1"]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": ["2", "1"]}} or c == {"a": {"b": ["1", "2"]}}


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
    assert c == {"a": {"b": [1, 2, 3, 4]}}

    a = {"a": [1, 2, 3]}
    b = {"a": [3, 4, 5]}
    c = merge({}, [a, b])
    assert c == {"a": [1, 2, 3, 4, 5]}


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


def test_merger_dict_single_list_values():
    # mixed dict

    a = {"a": {"b": [1]}}
    b = {"a": {"b": "2"}}
    assert merge({}, [a, b]) == {"a": {"b": [1, "2"]}}

    a = {"a": {"b": 1}}
    b = {"a": {"b": ["2"]}}
    assert merge({}, [a, b]) == {"a": {"b": [1, "2"]}}

    # int

    a = {"a": {"b": [1]}}
    b = {"a": {"b": 2}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, 2]}}

    a = {"a": {"b": 1}}
    b = {"a": {"b": [2]}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, 2]}}

    # float

    a = {"a": {"b": [.1]}}
    b = {"a": {"b": .2}}
    assert merge({}, [a, b]) == {"a": {"b": [.1, .2]}}

    a = {"a": {"b": .1}}
    b = {"a": {"b": [.2]}}
    assert merge({}, [a, b]) == {"a": {"b": [.1, .2]}}

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
    a = {"a": 1}
    b = {"a": {"b": 1}}
    c = merge({}, [a, b])
    assert c == {"a": {"b": [1, 2, 3, 4]}}

    # a = {"a": {"b": 1}}
    # b = {"a": 1}
    # c = merge({}, [a, b])
    # assert c == {"a": {"b": [1, 2, 3, 4]}}
