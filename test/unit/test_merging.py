import pytest

from tracardi.service.merging.merger import MergingStrategy, append


def test_append_simple_value_to_nonexistent_key():
    base = {}
    key = 'new_key'
    value = 'new_value'
    strategy = MergingStrategy(
        default_object_strategy='override'
    )

    result = append(base, key, value, strategy)

    assert result == {key: value}


def test_append_simple_value_to_existing_key():
    base = {'existing_key': 'existing_value'}
    key = 'existing_key'
    value = 'new_value'
    strategy = MergingStrategy(
        default_string_strategy='append'
    )

    result = append(base, key, value, strategy)

    assert set(result[key]) == {'existing_value', 'new_value'}


def test_append_simple_value_to_existing_key_list():
    key = 'existing_key'
    base = {key: ['existing_value']}
    value = 'new_value'
    strategy = MergingStrategy(
        default_list_strategy='append'
    )

    result = append(base, key, value, strategy)

    assert set(result[key]) == {'existing_value', 'new_value'}

    key = 'existing_key'
    base = {key: 'existing_value'}
    value = ['new_value']
    strategy = MergingStrategy(
        default_list_strategy='override',
        no_single_value_list = True
    )

    result = append(base, key, value, strategy)

    assert result[key] == 'new_value'

    key = 'existing_key'
    base = {key: 'existing_value'}
    value = ['new_value']
    strategy = MergingStrategy(
        default_list_strategy='override',
        no_single_value_list=False
    )

    result = append(base, key, value, strategy)

    assert result[key] == ['new_value']


def test_override_simple_value_to_existing_key_list():
    key = 'existing_key'
    base = {key: ['existing_value']}
    value = 'new_value'
    strategy = MergingStrategy(
        default_list_strategy='override'
    )

    result = append(base, key, value, strategy)

    assert result[key] == 'new_value'


def test_overwrite_simple_value_to_existing_key():
    key = 'existing_key'
    base = {key: 'existing_value'}
    value = 'new_value'
    strategy = MergingStrategy(
        default_string_strategy='override'
    )

    result = append(base, key, value, strategy)

    assert result[key] == 'new_value'


def test_append_value_to_existing_key_with_invalid_list():
    base = {'existing_key': [1, 2, 3]}
    key = 'existing_key'
    value = [4, {'invalid'}, 6]
    strategy = MergingStrategy()

    with pytest.raises(ValueError):
        append(base, key, value, strategy)


def test_append_value_to_existing_key_with_unknown_strategy():
    base = {'existing_key': 'existing_value'}
    key = 'existing_key'
    value = 'new_value'
    strategy = MergingStrategy(default_string_strategy='unknown')

    with pytest.raises(ValueError):
        append(base, key, value, strategy)
