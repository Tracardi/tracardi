from tracardi.service.list_default_value import list_value_at_index


def test_should_return_default_value_at_empty_index():
    item, data = list_value_at_index([], 0, {"a": 1})
    assert item == {"a": 1}
    assert data == [{"a": 1}]

    item, data = list_value_at_index(data, 1, {"a": 2})
    assert item == {"a": 2}
    assert data == [{"a": 1}, {"a": 2}]

    item, data = list_value_at_index(data, 1, {"a": 2})
    assert item == {"a": 2}
    assert data == [{"a": 1}, {"a": 2}]

    data[1]['b'] = 3

    item, data = list_value_at_index(data, 1, {"a": 2})
    assert item == {"a": 2, "b": 3}
    assert data == [{"a": 1}, {"a": 2, "b": 3}]
