from datetime import datetime, timedelta

from tracardi.domain.profile import ConsentRevoke
from tracardi.service.merging.merger import (merge as dict_merge, list_merge, get_conflicted_values,
                                             get_added_values, get_changed_values, MergingStrategy)


def test_merger():
    base = {
        "a": 1.0,
        "b": 2,
        "c": {"a1": 1},
        "d": "a",
        "e": None
    }

    dict_2 = {
        "a": 2,
        "c": {"a2": 0, "a1": 2},
        "d": "b",
        "e": "e"
    }
    result = dict_merge(base, [dict_2], MergingStrategy(
        make_lists_uniq=True,
        no_single_value_list=True,
        default_string_strategy='append'
    ))
    assert result['a'] == 3.0  # Numeric values are added
    assert result['b'] == 2
    assert result['c'] == {'a1': 3, 'a2': 0}
    assert set(result['d']) == {'a', 'b'}
    assert result['e'] == [None, 'e']

    assert set(get_conflicted_values(base, result)['d']) == {'a', 'b'}
    assert get_added_values(base, result) == {'c': {'a2': 0}}
    assert get_changed_values(base, result) == {'a': 3.0, 'c': {'a1': 3}}


def test_merger_on_duplicate_values():
    dict_1 = {
        "d": ["a", "a"]
    }

    dict_2 = {
        "d": []
    }

    result = dict_merge(dict_1, [dict_2], MergingStrategy(
        make_lists_uniq=False, no_single_value_list=False,
        default_string_strategy='append'
    ))
    assert result == {"d": ["a", "a"]}

    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=True, no_single_value_list=False,
                                                          default_string_strategy='append'))
    assert result == {"d": ["a"]}

    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=True, no_single_value_list=True,
                                                          default_string_strategy='append'))
    assert result == {"d": "a"}


def test_merger_on_list_of_number_values():
    dict_1 = {
        "d": [1]
    }

    dict_2 = {
        "d": 2
    }

    result = dict_merge(dict_1, [dict_2], MergingStrategy(
        make_lists_uniq=False,
        no_single_value_list=False,
        default_string_strategy='append'
    ))

    assert set(result['d']) == {1, 2}

    # ---

    dict_1 = {
        "d": 1
    }

    dict_2 = {
        "d": [2, 3]  # merge as if the field should be list. Threat 1 as list
    }

    result = dict_merge(dict_1, [dict_2], MergingStrategy(
        make_lists_uniq=False,
        no_single_value_list=False,
        default_string_strategy='append'
    ))

    assert set(result['d']) == {1, 2, 3}

    # ---

    dict_1 = {"a": {"d": [1]}}

    dict_2 = {
        "a": {"d": 2}
    }

    result = dict_merge(dict_1, [dict_2], MergingStrategy(
        make_lists_uniq=False,
        no_single_value_list=False,
        default_string_strategy='append'
    ))

    assert set(result['a']['d']) == {1, 2}


def test_merger_on_same_values():
    dict_1 = {
        "d": "a",
        "a": [1, 2, 3]
    }

    dict_2 = {
        "d": "a",
        "a": [1, 2, 3]
    }

    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=False, no_single_value_list=False,
                                                          default_string_strategy='append'))
    assert result == {"d": "a", "a": [1, 2, 3]}
    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=True, no_single_value_list=False,
                                                          default_string_strategy='append'))
    assert result == {"d": "a", "a": [1, 2, 3]}
    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=True, no_single_value_list=True,
                                                          default_string_strategy='append'))
    assert result == {"d": "a", "a": [1, 2, 3]}
    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=False, no_single_value_list=True,
                                                          default_string_strategy='append'))
    assert result == {"d": "a", "a": [1, 2, 3]}

    dict_1 = {
        "d": "a"
    }

    dict_2 = {
        "d": "b"
    }

    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=False, no_single_value_list=False,
                                                          default_string_strategy='append'))
    assert set(result['d']) == {'a', 'b'}
    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=True, no_single_value_list=False,
                                                          default_string_strategy='append'))
    assert set(result['d']) == {'a', 'b'}
    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=True, no_single_value_list=True,
                                                          default_string_strategy='append'))
    assert set(result['d']) == {'a', 'b'}
    result = dict_merge(dict_1, [dict_2], MergingStrategy(make_lists_uniq=False, no_single_value_list=True,
                                                          default_string_strategy='append'))
    assert set(result['d']) == {'a', 'b'}


def test_merging_dict_with_objects():
    consents1 = {"yyy": ConsentRevoke(revoke=datetime.utcnow())}
    consents2 = {"yyy": ConsentRevoke(revoke=None)}

    result = dict_merge(consents1, [consents2], MergingStrategy(make_lists_uniq=False, no_single_value_list=True,
                                                                default_string_strategy='append'))
    assert result == {"yyy": ConsentRevoke(revoke=None)}

    new_time = datetime.utcnow() + timedelta(seconds=3600)
    consents1 = {"yyy": datetime.utcnow()}
    consents2 = {"yyy": new_time}

    result = dict_merge(consents1, [consents2], MergingStrategy(make_lists_uniq=False, no_single_value_list=True,
                                                                default_string_strategy='append'))
    assert result['yyy'] == new_time


def test_merging_lists():
    dict_1 = [1, 2, 3]
    dict_2 = [3, 4, 5]

    result = list_merge(dict_1, dict_2, MergingStrategy(make_lists_uniq=False, no_single_value_list=True,
                                                        default_string_strategy='append'))
    assert result == [1, 2, 3, 3, 4, 5]

    result = list_merge(dict_1, dict_2, MergingStrategy(make_lists_uniq=True, no_single_value_list=True,
                                                        default_string_strategy='append'))
    assert result == [1, 2, 3, 4, 5]

    result = list_merge(dict_1, dict_2, MergingStrategy(make_lists_uniq=True, no_single_value_list=True,
                                                        default_string_strategy='append'))
    assert result == [1, 2, 3, 4, 5]

    # TODO should be fixed
    # result = list_merge(dict_1, dict_2, make_lists_uniq=False, no_single_value_list=False)
    # assert result == [1, 2, 3, 3, 4, 5]


def test_dict_with_ints():
    dict_1 = {"a": 1, "b": 2}
    dict_2 = {"a": 2, "c": -1}
    dict_3 = {"a": 2, "c": 1}

    result = dict_merge(dict_1, [dict_2, dict_3], MergingStrategy(make_lists_uniq=False, no_single_value_list=True,
                                                                  default_string_strategy='append'))
    assert result == {'a': 5, 'b': 2, 'c': 0}
    result = dict_merge(dict_1, [dict_2, dict_3], MergingStrategy(make_lists_uniq=True, no_single_value_list=True,
                                                                  default_string_strategy='append'))
    assert result == {'a': 5, 'b': 2, 'c': 0}
    result = dict_merge(dict_1, [dict_2, dict_3],
                        MergingStrategy(make_lists_uniq=False, no_single_value_list=False,
                                        default_string_strategy='append'))
    assert result == {'a': 5, 'b': 2, 'c': 0}
    result = dict_merge(dict_1, [dict_2, dict_3], MergingStrategy(make_lists_uniq=True, no_single_value_list=False,
                                                                  default_string_strategy='append'))
    assert result == {'a': 5, 'b': 2, 'c': 0}


def test_dict_override_numbers():
    dict_1 = {"a": 1, "b": 2}
    dict_2 = {"a": 2, "c": -1}
    dict_3 = {"a": 2, "c": 1}

    result = dict_merge(dict_1, [dict_2, dict_3],
                        MergingStrategy(make_lists_uniq=False,
                                        no_single_value_list=True,
                                        default_string_strategy='append',
                                        default_number_strategy='override'))
    assert result == {'a': 2, 'b': 2, 'c': 1}

    result = dict_merge(dict_1, [dict_2, dict_3],
                        MergingStrategy(make_lists_uniq=False,
                                        no_single_value_list=True,
                                        default_string_strategy='append',
                                        default_number_strategy='add'))
    assert result == {'a': 5, 'b': 2, 'c': 0}

    result = dict_merge(dict_1, [dict_2, dict_3],
                        MergingStrategy(make_lists_uniq=False,
                                        no_single_value_list=True,
                                        default_string_strategy='append',
                                        default_number_strategy='append'))
    assert result == {'a': [1, 2, 2], 'b': 2, 'c': [-1, 1]}


def test_override_strings():
    dict_1 = {"a": "1", "b": "2", "d": None}
    dict_2 = {"a": "2", "c": "-1"}
    dict_3 = {"a": "2", "c": "1", "d": "d"}

    result = dict_merge(dict_1, [dict_2, dict_3],
                        MergingStrategy(make_lists_uniq=False,
                                        no_single_value_list=True,
                                        default_string_strategy="override"))
    assert result == {'a': "2", 'b': "2", 'c': "1", "d": "d"}

    result = dict_merge(dict_1, [dict_2, dict_3],
                        MergingStrategy(make_lists_uniq=False,
                                        no_single_value_list=True,
                                        default_string_strategy="append"))
    assert result == {'a': ["1", "2", "2"], 'b': "2", 'c': ["-1", "1"], "d": [None, "d"]}

    dict_1 = {"d": 'a'}
    dict_2 = {"d": None}

    result = dict_merge(dict_1, [dict_2],
                        MergingStrategy(make_lists_uniq=False,
                                        no_single_value_list=True,
                                        default_string_strategy="override"))
    assert result == {"d": "a"}
