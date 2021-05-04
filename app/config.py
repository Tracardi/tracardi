import os


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


elastic = ElasticConfig(os.environ)

unomi_index = {
    "segment": "context-segment",
    "rule": "context-rule",
    "rulestats": "context-rulestats",
    "goal": "context-goal",
    "event": "context-event-*",
    "session": "context-session-*",
    "profile": "context-profile",
}

index = {
    "tokens": "tracardi-tokens",
    "segments": "tracardi-segments",
    "rules": "tracardi-rules",
    "goals": "tracardi-goals",
    "sources": "tracardi-sources",
}

unomi = {
    'host': os.environ['UNOMI_HOST'] if 'UNOMI_HOST' in os.environ else '127.0.0.1',
    'protocol': os.environ['UNOMI_PROTOCOL'] if 'UNOMI_PROTOCOL' in os.environ else 'http',
    'port': os.environ['UNOMI_PORT'] if 'UNOMI_PORT' in os.environ else 8181,
    'username': os.environ['UNOMI_USERNAME'] if 'UNOMI_USERNAME' in os.environ else 'karaf',
    'password': os.environ['UNOMI_PASSWORD'] if 'UNOMI_PASSWORD' in os.environ else 'karaf',
}
