from tracardi.service.notation.dot_accessor import DotAccessor


def test_wrong_source():
    dot = DotAccessor(profile={"a": {"id": 10, "c": {"d": 20}}})
    try:
        assert dot["payload@a.id"] == 10
    except Exception:
        assert True


def test_should_access_object_with_dollar():
    dot = DotAccessor(profile={"a": {"$id": 10, "$c": {"d": 20}}})
    assert dot["profile@a.$id"] == 10
    assert dot["profile@a.$c.d"] == 20


def test_should_validate_dot_notation():
    assert not DotAccessor.validate("invalid@dot.notation")
    assert DotAccessor.validate("event@properties.event-data.recipient")
    assert DotAccessor.validate("payload@dot.0.notation")
    assert DotAccessor.validate("payload@dot.0.$")
    assert DotAccessor.validate("payload@dot.0.*")
    assert DotAccessor.validate("payload@dot.0.$test")
    assert DotAccessor.validate("payload@dot.notation")
    assert DotAccessor.validate("payload@dot.notłóśćąation.@$#$%^&*")
    assert DotAccessor.validate("payload@dot.$notation")
    assert not DotAccessor.validate("invalid@dot.[0].notation")


def test_dot_accessor_3_dots():
    dot = DotAccessor(profile={"a": 1, "b": [1, 2]}, session={"b": 2}, event={"c": 1}, memory={"m": 0})
    a = dot['profile@...']
    assert isinstance(a, dict)


def test_dot_accessor():
    dot = DotAccessor(profile={"a": 1, "b": [1, 2]}, session={"b": 2}, event={"c": 1}, memory={"m": 0})
    a = dot['profile@...']
    b = dot['profile@b.1']
    c = dot['event@...']
    d = dot['profile@a']
    e = dot['string']
    m = dot['memory@m']

    assert a == {"a": 1, "b": [1, 2]}
    assert b == 2
    assert c == {"c": 1}
    assert d == 1
    assert e == 'string'
    assert m == 0


def test_dot_accessor_fail():
    dot = DotAccessor(profile={"a": None, "b": [1, 2]}, session={"b": 2}, event={"c": 1})
    a = dot['xxx@...']
    b = dot['xxx@b.1']
    c = dot['']
    d = dot['no_path']

    assert a == 'xxx@...'
    assert b == 'xxx@b.1'
    assert c == ''
    assert d == 'no_path'


def test_null_values():
    dot = DotAccessor(profile={"a": None}, session={"b": None}, event={"c": None}, memory={"d": None})
    a = dot['profile@a']
    b = dot['session@b']
    c = dot['event@c']
    d = dot['memory@d']

    assert a is None
    assert b is None
    assert c is None
    assert d is None


def test_should_cast_values():
    dot = DotAccessor(
        profile={"a": "1", "b": "false"},
        session={"f": "true"},
        event={"c": "null", "d": "None", "e": {"key": "1.02"}, "g": [1, 2, 3]},
        memory={"m": "true"}
    )

    casted_true_value = dot["`true`"]
    true_string = dot["true"]
    casted_false_value = dot["`false`"]
    false_string = dot["false"]
    casted_null_value = dot["`null`"]
    null_string = dot["null"]
    casted_none_value = dot["`none`"]
    none_string = dot["none"]
    casted_int_value = dot["`10`"]
    int_string = dot["10"]
    casted_float_value = dot["`4.16`"]
    float_string = dot["4.16"]
    uppercase_casted_true_value = dot["`TRUE`"]
    uppercase_true_string = dot["TRUE"]
    uppercase_casted_false_value = dot["`FALSE`"]
    uppercase_false_string = dot["FALSE"]
    uppercase_casted_null_value = dot["`NULL`"]
    uppercase_null_string = dot["NULL"]
    uppercase_casted_none_value = dot["`NONE`"]
    uppercase_none_string = dot["NONE"]
    a = dot["profile@a"]
    a_casted = dot["`profile@a`"]
    b = dot["profile@b"]
    b_casted = dot["`profile@b`"]
    c = dot["event@c"]
    c_casted = dot["`event@c`"]
    d = dot["event@d"]
    d_casted = dot["`event@d`"]
    e = dot["event@e.key"]
    e_casted = dot["`event@e.key`"]
    f = dot["session@f"]
    f_casted = dot["`session@f`"]
    array_value = dot["`event@g`"]
    object_value = dot["`event@e`"]
    memory_casted = dot["`memory@m`"]

    assert a == "1"
    assert a_casted == 1
    assert b == "false"
    assert b_casted is False
    assert c == "null"
    assert c_casted is None
    assert d == "None"
    assert d_casted is None
    assert e == "1.02"
    assert e_casted == 1.02
    assert f == "true"
    assert f_casted is True
    assert casted_true_value is True
    assert casted_false_value is False
    assert casted_null_value is None
    assert casted_none_value is None
    assert casted_int_value == 10
    assert casted_float_value == 4.16
    assert true_string == "true"
    assert false_string == "false"
    assert null_string == "null"
    assert none_string == "none"
    assert int_string == "10"
    assert float_string == "4.16"
    assert uppercase_casted_true_value is True
    assert uppercase_true_string == "TRUE"
    assert uppercase_casted_false_value is False
    assert uppercase_false_string == "FALSE"
    assert uppercase_casted_null_value is None
    assert uppercase_null_string == "NULL"
    assert uppercase_casted_none_value is None
    assert uppercase_none_string == "NONE"
    assert array_value == [1, 2, 3]
    assert object_value == {"key": "1.02"}
    assert memory_casted


def test_ampersand():
    dot = DotAccessor(
        profile={"@a": "1", "b": {"@a": 1}}
    )

    assert dot['profile@@a'] == '1'
    assert dot['profile@b.@a'] == 1