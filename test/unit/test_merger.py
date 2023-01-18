from tracardi.service.merger import merge as dict_merge, get_changed_values


def test_merger():
    base = {
        "a": 1,
        "b": 2,
        "c": {"a1": 1}
    }

    dict_2 = {
        "a": 2,
        "c": {"a2": 0, "a1": 2}
    }
    result = dict_merge(base, [dict_2])
    assert result['a'] == [1, 2]
    assert result['b'] == 2
    assert result == {'a': [1, 2], 'b': 2, 'c': {'a1': [1, 2], 'a2': 0}}

    assert get_changed_values(base, result) == {'a': [1, 2], 'c': {'a1': [1, 2]}}


