import os


class TracardiConfig:
    def __init__(self, env):
        self.track_debug = env['TRACK_DEBUG'] if 'TRACK_DEBUG' in env else False
        self.cache_profiles = env['CACHE_PROFILE'] if 'CACHE_PROFILE' in env else False
        self.sync_profile_tracks = env['SYNC_PROFILE_TRACKS'] if 'SYNC_PROFILE_TRACKS' in env else False
        self.storage_driver = env['STORAGE_DRIVER'] if 'STORAGE_DRIVER' in env else 'elastic'


class MemoryCacheConfig:
    def __init__(self, env):
        self.source_ttl = env['SOURCE_TTL'] if 'SOURCE_TTL' in env else 60


class ElasticConfig:

    def __init__(self, env):

        if 'ELASTIC_HOST' in env and not isinstance(env['ELASTIC_HOST'], str):
            raise ValueError("Env ELASTIC_HOST must be sting")

        if 'ELASTIC_HOST' in env and isinstance(env['ELASTIC_HOST'], str) and env['ELASTIC_HOST'].isnumeric():
            raise ValueError("Env ELASTIC_HOST must be sting")

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

        self.sql_translate_url = env[
            'ELASTIC_SQL_TRANSLATE_URL'] if 'ELASTIC_SQL_TRANSLATE_URL' in env else "/_sql/translate"
        self.sql_translate_method = env[
            'ELASTIC_SQL_TRANSLATE_METHOD'] if 'ELASTIC_SQL_TRANSLATE_METHOD' in env else "POST"
        self.refresh_profiles_after_save = env['ELASTIC_REFRESH_PROFILES_AFTER_SAVE'] \
            if 'ELASTIC_REFRESH_PROFILES_AFTER_SAVE' in env else False


class RedisConfig:

    def __init__(self, env):
        self.redis_host = env['REDIS_HOST'] if 'REDIS_HOST' in env else 'redis://localhost:6379'


redis_config = RedisConfig(os.environ)
elastic = ElasticConfig(os.environ)
memory_cache = MemoryCacheConfig(os.environ)
tracardi = TracardiConfig(os.environ)
