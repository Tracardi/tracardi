from tracardi.service.utils.parser import parse_accept_language


def test_single_language_tag():
    accept_language_header = "en;q=0.8"
    expected_result = [("en", 0.8)]
    assert parse_accept_language(accept_language_header) == expected_result


def test_multiple_language_tags():
    accept_language_header = "en;q=0.8,fr;q=0.5,de;q=0.6"
    expected_result = [("en", 0.8), ("fr", 0.5), ("de", 0.6)]
    assert parse_accept_language(accept_language_header) == expected_result


def test_language_tags_with_whitespace():
    accept_language_header = "en;q=0.8, fr;q=0.5, de;q=0.6"
    expected_result = [("en", 0.8), ("fr", 0.5), ("de", 0.6)]
    assert parse_accept_language(accept_language_header) == expected_result


def test_quality_values_in_different_formats():
    accept_language_header = "en;q=0.8,fr;q=1,int;q=0.5"
    expected_result = [("en", 0.8), ("fr", 1.0), ("int", 0.5)]
    assert parse_accept_language(accept_language_header) == expected_result

def test_quality_values_greater_than_1():
    accept_language_header = "en;q=2.5,fr;q=1.8,de;q=3"
    expected_result = [("en", 1.0), ("fr", 1.0), ("de", 1.0)]
    assert parse_accept_language(accept_language_header) == expected_result

def test_quality_values_less_than_0():
    accept_language_header = "en;q=-0.5,fr;q=-1,de;q=-2"
    expected_result = [("en", 0.0), ("fr", 0.0), ("de", 0.0)]
    assert parse_accept_language(accept_language_header) == expected_result
