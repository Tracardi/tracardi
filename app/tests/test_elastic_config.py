from app.config import ElasticConfig


def test_elastic_cluster_config():
    env = {
        "ELASTIC_HOST": "site-1.local,site-2,site-3.com",
        "ELASTIC_CAFILE": "cert.ca",
        "ELASTIC_SCHEME": "https",
        "ELASTIC_HTTP_AUTH_USERNAME": "user",
        "ELASTIC_HTTP_AUTH_PASSWORD": "pass",
        "ELASTIC_SNIFFER_TIMEOUT": 60,
        "ELASTIC_SNIFF_ON_START": True,
        "ELASTIC_SNIFF_ON_CONNECTION_FAIL": True,
        "ELASTIC_API_KEY": 'api-key',
        "ELASTIC_CLOUD_ID": 'cloud-id',
        "ELASTIC_MAX_CONN": 10

    }
    config = ElasticConfig(env)
    assert config.host == ['site-1.local', 'site-2', 'site-3.com']
    assert config.cafile == "cert.ca"
    assert config.scheme == 'https'
    assert config.http_auth_username == "user"
    assert config.http_auth_password == "pass"
    assert config.sniffer_timeout == 60
    assert config.api_key == ('id', 'api-key')
    assert config.cloud_id == 'cloud-id'
    assert config.maxsize == 10


def test_elastic_config_default_values():
    env = {}
    config = ElasticConfig(env)
    assert config.host == ['127.0.0.1']
    assert config.sniff_on_connection_fail is None
    assert config.sniff_on_start is None
    assert config.sniffer_timeout is None
    assert config.http_auth_username is None
    assert config.http_auth_password is None
    assert config.scheme is None
    assert config.cafile is None
    assert config.api_key is None
    assert config.cloud_id is None
    assert config.maxsize is None


def test_elastic_config_host_error():
    env = {
        "ELASTIC_HOST": 100,
    }
    try:
        ElasticConfig(env)
        assert False
    except ValueError:
        assert True

    env = {
        "ELASTIC_HOST": '100',
    }
    try:
        ElasticConfig(env)
        assert False
    except ValueError:
        assert True


def test_elastic_config_single_host():
    env = {
        "ELASTIC_HOST": 'localhost',
    }
    config = ElasticConfig(env)
    assert config.host == ['localhost']



