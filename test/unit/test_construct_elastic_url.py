from tracardi.service.url_constructor import construct_elastic_url


def test_should_return_url_with_credentials():
    url = construct_elastic_url('localhost', 'https', "user","pass")
    assert url == 'https://user:pass@localhost:9200'


def test_should_return_url_without_credentials():
    url = construct_elastic_url('localhost', 'https')
    assert url == 'https://localhost:9200'