from tracardi.service.valiadator import validate_email


def test_valid_email():
    assert validate_email("team-xxx+accountadmin@aaa.com") == True


def test_empty_string():
    assert validate_email("") == False


def test_multiple_at_symbols():
    assert validate_email("test@@example.com") == False


def test_at_symbol_at_end():
    assert validate_email("test@example.com@") == False