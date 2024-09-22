from tracardi.process_engine.action.v1.interest.utils import is_valid_string


def test_alphanumeric():
    assert is_valid_string("abc123") is True
    assert is_valid_string("abc_123") is True
    assert is_valid_string("abc-123") is True
    assert is_valid_string("abc@123") is False
    assert is_valid_string("___---") is False
    assert is_valid_string("_") is False
    assert is_valid_string("a,b,c") is True
    assert is_valid_string("a,b, c") is False
