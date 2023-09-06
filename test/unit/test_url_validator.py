from tracardi.service.utils.validators import is_valid_url


def test_valid_http_url():
    assert is_valid_url("http://www.example.com")


def test_valid_https_url():
    assert is_valid_url("https://www.example.com")


def test_valid_url_with_port_number():
    assert is_valid_url("http://www.example.com:8080")


def test_valid_url_with_query_parameters():
    assert is_valid_url("http://www.example.com?param1=value1&param2=value2")


def test_valid_url_with_fragment_identifier():
    assert is_valid_url("http://www.example.com#section1")


def test_invalid_url_with_no_scheme_or_netloc():
    assert is_valid_url("www.example.com") is False
