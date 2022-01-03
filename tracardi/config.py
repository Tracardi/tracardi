import logging
import os

ON_PREMISES = 'on-premises'
AWS_CLOUD = 'aws-cloud'


def _get_logging_level(level: str) -> int:
    level = level.upper()
    if level == 'DEBUG':
        return logging.DEBUG
    if level == 'INFO':
        return logging.INFO
    if level == 'WARNING' or level == "WARN":
        return logging.WARNING
    if level == 'ERROR':
        return logging.ERROR

    return logging.WARNING


class TracardiConfig:
    def __init__(self, env):
        self.track_debug = (env['TRACK_DEBUG'].lower() == 'yes') if 'TRACK_DEBUG' in env else False
        self.cache_profiles = env['CACHE_PROFILE'] if 'CACHE_PROFILE' in env else False
        self.sync_profile_tracks = (env['SYNC_PROFILE_TRACKS'].lower() == 'yes') if 'SYNC_PROFILE_TRACKS' in env else False
        self.storage_driver = env['STORAGE_DRIVER'] if 'STORAGE_DRIVER' in env else 'elastic'
        self.logging_level = _get_logging_level(env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in env else logging.WARNING
        self.version = '0.6.1'


class MemoryCacheConfig:
    def __init__(self, env):
        self.source_ttl = int(env['SOURCE_TTL']) if 'SOURCE_TTL' in env else 60
        self.tags_ttl = int(env['TAGS_TTL']) if 'TAGS_TTL' in env else 60


class ElasticConfig:

    def __init__(self, env):

        if 'ELASTIC_HOSTING' in env and not isinstance(env['ELASTIC_HOSTING'], str):
            raise ValueError("Env ELASTIC_HOSTING must be sting")

        if 'ELASTIC_HOST' in env and not isinstance(env['ELASTIC_HOST'], str):
            raise ValueError("Env ELASTIC_HOST must be sting")

        if 'ELASTIC_HOST' in env and isinstance(env['ELASTIC_HOST'], str) and env['ELASTIC_HOST'].isnumeric():
            raise ValueError("Env ELASTIC_HOST must be sting")

        self.hosting = env['ELASTIC_HOSTING'] if 'ELASTIC_HOSTING' in env else ON_PREMISES  # Possible values ON_PREMISES|AWS_CLOUD
        self.host = env['ELASTIC_HOST'] if 'ELASTIC_HOST' in env else '127.0.0.1'
        self.host = self.host.split(",")
        self.sniff_on_start = env['ELASTIC_SNIFF_ON_START'] if 'ELASTIC_SNIFF_ON_START' in env else None
        self.sniff_on_connection_fail = env[
            'ELASTIC_SNIFF_ON_CONNECTION_FAIL'] if 'ELASTIC_SNIFF_ON_CONNECTION_FAIL' in env else None
        self.sniffer_timeout = env['ELASTIC_SNIFFER_TIMEOUT'] if 'ELASTIC_SNIFFER_TIMEOUT' in env else None
        self.http_auth_username = env['ELASTIC_HTTP_AUTH_USERNAME'] if 'ELASTIC_HTTP_AUTH_USERNAME' in env else None
        self.http_auth_password = env['ELASTIC_HTTP_AUTH_PASSWORD'] if 'ELASTIC_HTTP_AUTH_PASSWORD' in env else None
        self.scheme = env['ELASTIC_SCHEME'] if 'ELASTIC_SCHEME' in env else None
        self.cafile = env['ELASTIC_CAFILE'] if 'ELASTIC_CAFILE' in env else None
        self.api_key = ('id', env['ELASTIC_API_KEY']) if 'ELASTIC_API_KEY' in env else None
        self.cloud_id = env['ELASTIC_CLOUD_ID'] if 'ELASTIC_CLOUD_ID' in env else None
        self.maxsize = env['ELASTIC_MAX_CONN'] if 'ELASTIC_MAX_CONN' in env else None
        self.http_compress = env['ELASTIC_HTTP_COMPRESS'] if 'ELASTIC_HTTP_COMPRESS' in env else None
        self.verify_certs = (env['ELASTIC_VERIFY_CERTS'].lower() == 'yes') if 'ELASTIC_VERIFY_CERTS' in env else None

        self.refresh_profiles_after_save = (env['ELASTIC_REFRESH_PROFILES_AFTER_SAVE'].lower() == 'yes') \
            if 'ELASTIC_REFRESH_PROFILES_AFTER_SAVE' in env else False
        self.logging_level = _get_logging_level(env['ELASTIC_LOGGING_LEVEL']) if 'ELASTIC_LOGGING_LEVEL' in env \
            else logging.WARNING

        # AWS env variables

        self.aws_access_key_id = env['AWS_ACCESS_KEY_ID'] if 'AWS_ACCESS_KEY_ID' in env else None
        self.aws_secret_access_key = env['AWS_SECRET_ACCESS_KEY'] if 'AWS_SECRET_ACCESS_KEY' in env else None
        self.aws_region = env['AWS_REGION'] if 'AWS_REGION' in env else None


class RedisConfig:

    def __init__(self, env):
        self.redis_host = env['REDIS_HOST'] if 'REDIS_HOST' in env else 'redis://localhost:6379'


redis_config = RedisConfig(os.environ)
elastic = ElasticConfig(os.environ)
memory_cache = MemoryCacheConfig(os.environ)
tracardi = TracardiConfig(os.environ)
