from tracardi.process_engine.action.v1.interest.utils import is_valid_string


def test_alphanumeric():
    assert is_valid_string("abc123") == True
    assert is_valid_string("abc_123") == True
    assert is_valid_string("abc-123") == True
    assert is_valid_string("abc@123") == False
    assert is_valid_string("___---") == False
    assert is_valid_string("_") == False