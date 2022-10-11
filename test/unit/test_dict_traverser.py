from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.notation.dot_accessor import DotAccessor


def test_dot_traverser():
    template = {
        "x": {
            "a": "session@...",
            "b": {"x": [1]},
            "c": [111, 222, "profile@a"],
            "d": {"q": {"z": 11, "e": 22}}
        }
    }

    dot = DotAccessor(profile={"a": [1, 2], "b": [1, 2]}, session={"b": 2}, event={})
    t = DictTraverser(dot)
    result = t.reshape(reshape_template=template)

    assert result['x']['a'] == {'b': 2}
    assert result['x']['b'] == {'x': [1]}
    assert result['x']['c'] == [111, 222, [1, 2]]
    assert result['x']['d'] == {"q": {"z": 11, "e": 22}}


def test_dot_traverser_no_value_remove():
    template = {
        "x": {
            "a": "session@...",  # Session does not exist
            "b": {"x": [1]},
            "c": [111, 222, "profile@a"],  # Profile does not exist
            "d": {"q": {"z": 11, "e": 22}}
        }
    }

    # Session does not exist
    dot = DotAccessor(profile={"b": [1, 2]}, event={})
    t = DictTraverser(dot, default=None, include_none=False)
    result = t.reshape(reshape_template=template)

    assert result['x']['b'] == {'x': [1]}
    assert result['x']['c'] == [111, 222]
    assert result['x']['d'] == {"q": {"z": 11, "e": 22}}


def test_dot_traverser_no_value_default():
    template = {
        "x": {
            "a": "session@...",  # Session does not exist
            "b": {"x": [1]},
            "c": [111, 222, "profile@a"],  # Profile does not exist
            "d": {"q": {"z": 11, "e": 22}},
            "m": "`memory@a`"
        }
    }

    # Session does not exist
    dot = DotAccessor(profile={"b": [1, 2]}, event={}, memory={"a": "true"})
    t = DictTraverser(dot, default=None)
    result = t.reshape(reshape_template=template)

    assert result['x']['a'] == {}
    assert result['x']['b'] == {'x': [1]}
    assert result['x']['c'] == [111, 222, None]
    assert result['x']['d'] == {"q": {"z": 11, "e": 22}}
    assert result['x']['m'] is True


def test_dot_traverser_optional_values():
    template = {
        "x": {
            "a?": "session@...",  # Session does not exist
            "c?": [111, "profile@b", "profile@a"],  # Profile@a does not exist
            "d": {"not-exists?": "profile@a", "exists?": "profile@b"}
        }
    }

    dot = DotAccessor(profile={"b": [1, 2]}, event={})
    t = DictTraverser(dot)
    result = t.reshape(reshape_template=template)

    assert 'a' not in result['x']
    assert result['x']['c'] == [111, [1, 2]]
    assert result['x']['d'] == {'exists': [1, 2]}


def test_dot_traverser_no_values_throw_error():
    template = {
        "x": {
            "a": "session@...",  # Session does not exist
            "c": [111, "profile@b", "profile@a"],  # Profile@a does not exist
            "d": {"not-exists?": "profile@a", "exists": "profile@b"}
        }
    }

    dot = DotAccessor(profile={"b": [1, 2]}, event={})
    t = DictTraverser(dot)
    try:
        t.reshape(reshape_template=template)
        assert False
    except KeyError:
        assert True
