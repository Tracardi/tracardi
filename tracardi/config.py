import logging
import os

import yaml

from tracardi.domain.version import Version
from tracardi.domain.yaml_config import YamlConfig

VERSION = '0.7.4-dev'
NAME = os.environ.get('INSTANCE_PREFIX', None)


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
        self.env = env
        self.track_debug = (env['TRACK_DEBUG'].lower() == 'yes') if 'TRACK_DEBUG' in env else False
        self.save_logs = (env['SAVE_LOGS'].lower() == 'yes') if 'SAVE_LOGS' in env else True
        self.monitor_logs_event_type = env['MONITOR_LOGS_EVENT_TYPE'].lower().replace(" ", "-") \
            if 'MONITOR_LOGS_EVENT_TYPE' in env else None
        self.cache_profiles = (env['CACHE_PROFILE'].lower() == 'yes') if 'CACHE_PROFILE' in env else False
        self.sync_profile_tracks = (
                env['SYNC_PROFILE_TRACKS'].lower() == 'yes') if 'SYNC_PROFILE_TRACKS' in env else False
        self.sync_profile_tracks_max_repeats = int(
            env['SYNC_PROFILE_TRACKS_MAX_REPEATS']) if 'SYNC_PROFILE_TRACKS_MAX_REPEATS' in env else 10
        self.sync_profile_tracks_wait = int(
            env['SYNC_PROFILE_TRACKS_WAIT']) if 'SYNC_PROFILE_TRACKS_WAIT' in env else 1
        self.postpone_destination_sync = int(
            env['POSTPONE_DESTINATION_SYNC']) if 'POSTPONE_DESTINATION_SYNC' in env else 20
        self.storage_driver = env['STORAGE_DRIVER'] if 'STORAGE_DRIVER' in env else 'elastic'
        self.query_language = env['QUERY_LANGUAGE'] if 'QUERY_LANGUAGE' in env else 'kql'
        self.tracardi_pro_host = env['TRACARDI_PRO_HOST'] if 'TRACARDI_PRO_HOST' in env else 'pro.tracardi.com'
        self.tracardi_pro_port = int(env['TRACARDI_PRO_PORT']) if 'TRACARDI_PRO_PORT' in env else 40000
        self.tracardi_scheduler_host = env[
            'TRACARDI_SCHEDULER_HOST'] if 'TRACARDI_SCHEDULER_HOST' in env else 'scheduler.tracardi.com'
        self.logging_level = _get_logging_level(env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in env else logging.WARNING
        self.version = Version(version=VERSION, name=NAME)
        self.installation_token = env.get('INSTALLATION_TOKEN', '')
        self._config = None
        self._unset_secrets()

    @property
    def config(self) -> YamlConfig:
        if not self._config:
            config = self.env.get('CONFIG', 'config.yaml')
            with open(config, "r") as stream:
                config = yaml.safe_load(stream)
                self._config = YamlConfig(**config)
        return self._config

    def _unset_secrets(self):
        self.env['INSTALLATION_TOKEN'] = ""


class MemoryCacheConfig:
    def __init__(self, env):
        self.source_ttl = int(env['SOURCE_TTL']) if 'SOURCE_TTL' in env else 60
        self.tags_ttl = int(env['TAGS_TTL']) if 'TAGS_TTL' in env else 60
        self.event_validator_ttl = int(env['EVENT_VALIDATOR_TTL']) if 'EVENT_VALIDATOR_TTL' in env else 180


class ElasticConfig:

    def __init__(self, env):
        self.env = env
        self.replicas = env['ELASTIC_INDEX_REPLICAS'] if 'ELASTIC_INDEX_REPLICAS' in env else "1"
        self.shards = env['ELASTIC_INDEX_SHARDS'] if 'ELASTIC_INDEX_SHARDS' in env else "5"
        self.sniff_on_start = env['ELASTIC_SNIFF_ON_START'] if 'ELASTIC_SNIFF_ON_START' in env else None
        self.sniff_on_connection_fail = env[
            'ELASTIC_SNIFF_ON_CONNECTION_FAIL'] if 'ELASTIC_SNIFF_ON_CONNECTION_FAIL' in env else None
        self.sniffer_timeout = env['ELASTIC_SNIFFER_TIMEOUT'] if 'ELASTIC_SNIFFER_TIMEOUT' in env else None
        self.ca_file = env['ELASTIC_CA_FILE'] if 'ELASTIC_CA_FILE' in env else None
        self.api_key_id = env['ELASTIC_API_KEY_ID'] if 'ELASTIC_API_KEY_ID' in env else None
        self.api_key = env['ELASTIC_API_KEY'] if 'ELASTIC_API_KEY' in env else None
        self.cloud_id = env['ELASTIC_CLOUD_ID'] if 'ELASTIC_CLOUD_ID' in env else None
        self.maxsize = env['ELASTIC_MAX_CONN'] if 'ELASTIC_MAX_CONN' in env else None
        self.http_compress = env['ELASTIC_HTTP_COMPRESS'] if 'ELASTIC_HTTP_COMPRESS' in env else None
        self.verify_certs = (env['ELASTIC_VERIFY_CERTS'].lower() == 'yes') if 'ELASTIC_VERIFY_CERTS' in env else None

        self.refresh_profiles_after_save = (env['ELASTIC_REFRESH_PROFILES_AFTER_SAVE'].lower() == 'yes') \
            if 'ELASTIC_REFRESH_PROFILES_AFTER_SAVE' in env else False
        self.logging_level = _get_logging_level(env['ELASTIC_LOGGING_LEVEL']) if 'ELASTIC_LOGGING_LEVEL' in env \
            else logging.WARNING
        self.host = self.get_host()
        self.http_auth_username = self.env.get('ELASTIC_HTTP_AUTH_USERNAME', None)
        self.http_auth_password = self.env.get('ELASTIC_HTTP_AUTH_PASSWORD', None)
        self.scheme = self.env.get('ELASTIC_SCHEME', 'http')

        self._unset_credentials()

    def get_host(self):
        hosts = self.env.get('ELASTIC_HOST', 'http://localhost:9200')

        if not isinstance(hosts, str) or hosts.isnumeric():
            raise ValueError("Env ELASTIC_HOST must be sting")

        if not hosts:
            raise ValueError("ELASTIC_HOST environment variable not set.")
        return hosts.split(",")

    def _unset_credentials(self):
        self.env['ELASTIC_HOST'] = ""
        if 'ELASTIC_HTTP_AUTH_USERNAME' in self.env:
            del self.env['ELASTIC_HTTP_AUTH_USERNAME']
        if 'ELASTIC_HTTP_AUTH_PASSWORD' in self.env:
            del self.env['ELASTIC_HTTP_AUTH_PASSWORD']

    def has(self, prop):
        return "Set" if getattr(self, prop, None) else "Unset"


class RedisConfig:

    def __init__(self, env):
        self.env = env
        self.redis_host = env['REDIS_HOST'] if 'REDIS_HOST' in env else 'redis://localhost:6379'
        self.redis_password = env.get('REDIS_PASSWORD', None)
        self._unset_credentials()

    def get_redis_with_password(self):
        if not self.redis_host.startswith('redis://'):
            self.redis_host = f"redis://{self.redis_host}"
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host[8:]}"
        return self.redis_host

    def _unset_credentials(self):
        if 'REDIS_HOST' in self.env:
            del self.env['REDIS_HOST']
        if 'REDIS_PASSWORD' in self.env:
            del self.env['REDIS_PASSWORD']


redis_config = RedisConfig(os.environ)
elastic = ElasticConfig(os.environ)
memory_cache = MemoryCacheConfig(os.environ)
tracardi = TracardiConfig(os.environ)
