import os
from ssl import create_default_context


class RedisConfig:

    def __init__(self, env):
        self.redis_host = env['REDIS_HOST'] if 'REDIS_HOST' in env else 'redis://localhost:6379'
        self.redis_password = env['REDIS_PASSWORD'] if 'REDIS_PASSWORD' in env else None

    def get_redis_with_password(self):
        if not self.redis_host.startswith('redis://'):
            self.redis_host = f"redis://{self.redis_host}"
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host[8:]}"
        return self.redis_host


class ElasticSearchConfig:

    def __init__(self, env):
        self.hosts = env['ELASTIC_HOST'].split(",") if 'ELASTIC_HOST' in env else None
        self.scheme = env['ELASTIC_SCHEME'] if 'ELASTIC_SCHEME' in env else 'http'
        self.sniffer_timeout = env['ELASTIC_SNIFFER_TIMEOUT'] if 'ELASTIC_SNIFFER_TIMEOUT' in env else None
        self.sniff_on_connection_fail = env[
            'ELASTIC_SNIFF_ON_CONNECTION_FAIL'] if 'ELASTIC_SNIFF_ON_CONNECTION_FAIL' in env else None
        self.sniff_on_start = env['ELASTIC_SNIFF_ON_START'] if 'ELASTIC_SNIFF_ON_START' in env else None
        self.maxsize = env['ELASTIC_MAX_CONN'] if 'ELASTIC_MAX_CONN' in env else None
        self.ca_file = env['ELASTIC_CA_FILE'] if 'ELASTIC_CA_FILE' in env else None
        self.http_auth_username = env['ELASTIC_HTTP_AUTH_USERNAME'] if 'ELASTIC_HTTP_AUTH_USERNAME' in env else None
        self.http_auth_password = env['ELASTIC_HTTP_AUTH_PASSWORD'] if 'ELASTIC_HTTP_AUTH_PASSWORD' in env else None
        self.cloud_id = env['ELASTIC_CLOUD_ID'] if 'ELASTIC_CLOUD_ID' in env else None
        self.api_key_id = env['ELASTIC_API_KEY_ID'] if 'ELASTIC_API_KEY_ID' in env else None
        self.api_key = env['ELASTIC_API_KEY'] if 'ELASTIC_API_KEY' in env else None
        self.http_compress = env['ELASTIC_HTTP_COMPRESS'] if 'ELASTIC_HTTP_COMPRESS' in env else None
        self.verify_certs = (env['ELASTIC_VERIFY_CERTS'].lower() == 'yes') if 'ELASTIC_VERIFY_CERTS' in env else None

    def get_elasticsearch_config(self) -> dict:

        config = {}

        if self.hosts:
            config['hosts'] = self.hosts
        if self.scheme:
            config['scheme'] = self.scheme
        if self.sniffer_timeout:
            config['sniffer_timeout'] = self.sniffer_timeout
        if self.sniff_on_start:
            config['sniff_on_start'] = self.sniff_on_start
        if self.sniff_on_connection_fail:
            config['sniff_on_connection_fail'] = self.sniff_on_connection_fail
        if self.maxsize:
            config['maxsize'] = self.maxsize

        if self.ca_file:
            context = create_default_context(cafile=self.ca_file)
            config['ssl_context'] = context

        if self.http_auth_password and self.http_auth_username:
            config['http_auth'] = (self.http_auth_username, self.http_auth_password)

        if self.cloud_id:
            config['cloud_id'] = self.cloud_id

        if self.api_key and self.api_key_id:
            config['api_key'] = (self.api_key_id, self.api_key)

        if self.http_compress:
            config['http_compress'] = self.http_compress

        if self.verify_certs is not None:
            config['verify_certs'] = self.verify_certs

        return config


redis_config = RedisConfig(os.environ)
elasticsearch_config = ElasticSearchConfig(os.environ)
