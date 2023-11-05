from tracardi.service.utils.validators import is_valid_hex


def test_is_valid_hex():
    assert is_valid_hex("af")
    assert is_valid_hex("00")
    assert not is_valid_hex("ag")
