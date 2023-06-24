import logging
import os
from hashlib import md5

import yaml

from tracardi.domain.version import Version
from tracardi.domain.yaml_config import YamlConfig
from tracardi.service.utils.validators import is_valid_url

VERSION = os.environ.get('_DEBUG_VERSION', '0.8.1')
TENANT_NAME = os.environ.get('TENANT_NAME', None)


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


class MemoryCacheConfig:
    def __init__(self, env):
        self.event_to_profile_coping_ttl = int(env['EVENT_TO_PROFILE_COPY_CACHE_TTL']) if 'EVENT_TO_PROFILE_COPY_CACHE_TTL' in env else 2
        self.source_ttl = int(env['SOURCE_CACHE_TTL']) if 'SOURCE_CACHE_TTL' in env else 2
        self.session_cache_ttl = int(env['SESSION_CACHE_TTL']) if 'SESSION_CACHE_TTL' in env else 2
        self.event_validation_cache_ttl = int(
            env['EVENT_VALIDATION_CACHE_TTL']) if 'EVENT_VALIDATION_CACHE_TTL' in env else 2
        self.event_metadata_cache_ttl = int(env['EVENT_METADATA_CACHE_TTL']) if 'EVENT_METADATA_CACHE_TTL' in env else 2
        self.event_destination_cache_ttl = int(
            env['EVENT_DESTINATION_CACHE_TTL']) if 'EVENT_DESTINATION_CACHE_TTL' in env else 2
        self.profile_destination_cache_ttl = int(
            env['PROFILE_DESTINATION_CACHE_TTL']) if 'PROFILE_DESTINATION_CACHE_TTL' in env else 2


class ElasticConfig:

    def __init__(self, env):
        self.env = env
        self.replicas = env['ELASTIC_INDEX_REPLICAS'] if 'ELASTIC_INDEX_REPLICAS' in env else "1"
        self.shards = env['ELASTIC_INDEX_SHARDS'] if 'ELASTIC_INDEX_SHARDS' in env else "3"
        self.conf_shards = env['ELASTIC_CONF_INDEX_SHARDS'] if 'ELASTIC_CONF_INDEX_SHARDS' in env else "1"
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

        self.host = self.get_host()
        self.http_auth_username = self.env.get('ELASTIC_HTTP_AUTH_USERNAME', None)
        self.http_auth_password = self.env.get('ELASTIC_HTTP_AUTH_PASSWORD', None)
        self.scheme = self.env.get('ELASTIC_SCHEME', 'http')
        self.query_timeout = int(env['ELASTIC_QUERY_TIMEOUT']) if 'ELASTIC_QUERY_TIMEOUT' in env else 12
        self.save_pool = int(env['ELASTIC_SAVE_POOL']) if 'ELASTIC_SAVE_POOL' in env else 0
        self.save_pool_ttl = int(env['ELASTIC_SAVE_POOL_TTL']) if 'ELASTIC_SAVE_POOL_TTL' in env else 5
        self.logging_level = _get_logging_level(
            env['ELASTIC_LOGGING_LEVEL']) if 'ELASTIC_LOGGING_LEVEL' in env else logging.ERROR

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
        # self._unset_credentials()

    def get_redis_with_password(self):
        return self.get_redis_uri(self.redis_host, password=self.redis_password)

    @staticmethod
    def get_redis_uri(host, user=None, password=None, protocol="redis", database="0"):
        if not host.startswith('redis://'):
            host = f"{protocol}://{host}/{database}"
        if user and password:
            return f"{protocol}://{user}:{password}@{host[8:]}/{database}"
        elif password:
            return f"{protocol}://:{password}@{host[8:]}/{database}"
        return host

    # Tych danych potrebuje jeszcze worker moze tam można je wykasować
    # def _unset_credentials(self):
    #     if 'REDIS_HOST' in self.env:
    #         del self.env['REDIS_HOST']
    #     if 'REDIS_PASSWORD' in self.env:
    #         del self.env['REDIS_PASSWORD']


redis_config = RedisConfig(os.environ)
elastic = ElasticConfig(os.environ)
memory_cache = MemoryCacheConfig(os.environ)


class TracardiConfig:
    def __init__(self, env):
        self.env = env
        _production = (env['PRODUCTION'].lower() == 'yes') if 'PRODUCTION' in env else False
        self.track_debug = (env['TRACK_DEBUG'].lower() == 'yes') if 'TRACK_DEBUG' in env else False
        self.save_logs = (env['SAVE_LOGS'].lower() == 'yes') if 'SAVE_LOGS' in env else True
        self.cache_profiles = (env['CACHE_PROFILE'].lower() == 'yes') if 'CACHE_PROFILE' in env else False
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
        self.server_logging_level = _get_logging_level(
            env['SERVER_LOGGING_LEVEL']) if 'SERVER_LOGGING_LEVEL' in env else logging.WARNING
        self.multi_tenant = env.get('MULTI_TENANT', "no") == 'yes'
        self.multi_tenant_manager_url = env.get('MULTI_TENANT_MANAGER_URL', None)
        self.multi_tenant_manager_api_key = env.get('MULTI_TENANT_MANAGER_API_KEY', None)
        self.version: Version = Version(version=VERSION, name=TENANT_NAME, production=_production)
        self.installation_token = env.get('INSTALLATION_TOKEN', 'tracardi')
        self.fingerprint = md5(f"aks843jfd8trn{self.installation_token}-{elastic.host}".encode()).hexdigest()
        self.cardio_source = md5(
            f"akkdskjd-askmdj-jdff{self.installation_token}-3039djn-{elastic.host}".encode()).hexdigest()
        self._config = None
        self._unset_secrets()

        if self.multi_tenant and (self.multi_tenant_manager_url is None or self.multi_tenant_manager_api_key is None):
            if self.multi_tenant_manager_url is None:
                raise AssertionError('No MULTI_TENANT_MANAGER_URL set for MULTI_TENANT mode. Either set '
                                     'the MULTI_TENANT_MANAGER_URL or set MULTI_TENANT to "no"')

            if self.multi_tenant_manager_api_key is None:
                raise AssertionError('No MULTI_TENANT_MANAGER_API_KEY set for MULTI_TENANT mode. Either set '
                                     'the MULTI_TENANT_MANAGER_API_KEY or set MULTI_TENANT to "no"')

        if self.multi_tenant and not is_valid_url(self.multi_tenant_manager_url):
            raise AssertionError('Env MULTI_TENANT_MANAGER_URL is not valid URL.')

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


tracardi = TracardiConfig(os.environ)
