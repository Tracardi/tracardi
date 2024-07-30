import logging
import os
from hashlib import md5

import yaml

from tracardi.domain import ExtraInfo
from tracardi.domain.version import Version
from tracardi.domain.yaml_config import YamlConfig
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.logging.tools import _get_logging_level
from tracardi.service.singleton import Singleton
from tracardi.service.utils.environment import get_env_as_int, get_env_as_bool
from tracardi.service.utils.validators import is_valid_url

VERSION = os.environ.get('_DEBUG_VERSION', '1.0.x')
TENANT_NAME = os.environ.get('TENANT_NAME', None)

logger = get_logger(__name__)


class MemoryCacheConfig:
    def __init__(self, env):
        self.event_to_profile_coping_ttl = get_env_as_int('EVENT_TO_PROFILE_COPY_CACHE_TTL', 5)
        self.source_ttl = get_env_as_int('SOURCE_CACHE_TTL', 5)
        self.session_cache_ttl = get_env_as_int('SESSION_CACHE_TTL', 5)
        self.event_validation_cache_ttl = get_env_as_int('EVENT_VALIDATION_CACHE_TTL', 15)
        self.event_metadata_cache_ttl = get_env_as_int('EVENT_METADATA_CACHE_TTL', 15)
        self.event_destination_cache_ttl = get_env_as_int('EVENT_DESTINATION_CACHE_TTL', 5)
        self.profile_destination_cache_ttl = get_env_as_int('PROFILE_DESTINATION_CACHE_TTL', 5)
        self.data_compliance_cache_ttl = get_env_as_int('DATA_COMPLIANCE_CACHE_TTL', 5)
        self.trigger_rule_cache_ttl = get_env_as_int('TRIGGER_RULE_CACHE_TTL', 15)


class MysqlConfig:

    def __init__(self, env):
        self.env = env
        self.mysql_host = env.get('MYSQL_HOST', "localhost")
        self.mysql_username = env.get('MYSQL_USERNAME', "root")
        self.mysql_password = env.get('MYSQL_PASSWORD', "root")
        self.mysql_schema = env.get('MYSQL_SCHEMA', "mysql+aiomysql://")
        self.mysql_schema_sync = env.get('MYSQL_SCHEMA', "mysql+pymysql://")
        self.mysql_port = env.get('MYSQL_PORT', 3306)
        self.mysql_database = env.get('MYSQL_DATABASE', "tracardi")
        self.mysql_echo = env.get('MYSQL_ECHO', "no") == "yes"

        self.mysql_database = self.mysql_database.strip(" /")

        self.mysql_database_uri = self.uri(async_driver=True)
        self.mysql_database_uri_with_db = f"{self.mysql_database_uri}/{self.mysql_database}"


    def _get_schema(self, async_driver:bool=True):
        if async_driver:
            return self.mysql_schema
        return self.mysql_schema_sync

    def uri(self, async_driver:bool=True) -> str:
        if self.mysql_username and self.mysql_password:
            _creds = f"{self.mysql_username}:{self.mysql_password}"
        elif self.mysql_username:
            _creds = f"{self.mysql_username}:"
        else:
            _creds = ""

        if _creds:
            uri = f"{self._get_schema(async_driver)}{_creds}@{self.mysql_host}:{self.mysql_port}"
        else:
            uri = f"{self._get_schema(async_driver)}{self.mysql_host}:{self.mysql_port}"

        return uri.strip(" /")

class StarRocksConfig:
    def __init__(self, env):
        self.env = env
        self.starrocks_host = env.get('STARROCKS_HOST', "localhost")
        self.starrocks_username = env.get('STARROCKS_USERNAME', "root")
        self.starrocks_password = env.get('STARROCKS_PASSWORD', "root")
        self.starrocks_schema = env.get('STARROCKS_SCHEMA', "mysql+aiomysql://")
        self.starrocks_schema_sync = env.get('STARROCKS_SCHEMA', "mysql+pymysql://")
        self.starrocks_port = env.get('STARROCKS_PORT', 9030)
        self.starrocks_database = env.get('STARROCKS_DATABASE', "tracardi")
        self.starrocks_echo = env.get('STARROCKS_ECHO', "no") == "yes"

        self.starrocks_database = self.starrocks_database.strip(" /")

        self.starrocks_database_uri = self.uri(async_driver=True)
        self.starrocks_database_uri_with_db = f"{self.starrocks_database_uri}/{self.starrocks_database}"


    def _get_schema(self, async_driver:bool=True):
        if async_driver:
            return self.starrocks_schema
        return self.starrocks_schema_sync

    def uri(self, async_driver:bool=True) -> str:
        if self.starrocks_username and self.starrocks_password:
            _creds = f"{self.starrocks_username}:{self.starrocks_password}"
        elif self.starrocks_username:
            _creds = f"{self.starrocks_username}:"
        else:
            _creds = ""

        if _creds:
            uri = f"{self._get_schema(async_driver)}{_creds}@{self.starrocks_host}:{self.starrocks_port}"
        else:
            uri = f"{self._get_schema(async_driver)}{self.starrocks_host}:{self.starrocks_port}"

        return uri.strip(" /")

class ElasticConfig:

    def __init__(self, env):
        self.env = env
        self.unset_credentials = get_env_as_bool('UNSET_CREDENTIALS', "off")
        self.replicas = env.get('ELASTIC_INDEX_REPLICAS', "1")
        self.shards = env.get('ELASTIC_INDEX_SHARDS', "3")
        self.conf_shards = env.get('ELASTIC_CONF_INDEX_SHARDS', "1")
        self.sniff_on_start = env.get('ELASTIC_SNIFF_ON_START', None)
        self.sniff_on_connection_fail = env.get('ELASTIC_SNIFF_ON_CONNECTION_FAIL', None)
        self.sniffer_timeout = env.get('ELASTIC_SNIFFER_TIMEOUT', None)
        self.ca_file = env.get('ELASTIC_CA_FILE', None)
        self.api_key_id = env.get('ELASTIC_API_KEY_ID', None)
        self.api_key = env.get('ELASTIC_API_KEY', None)
        self.cloud_id = env['ELASTIC_CLOUD_ID'] if 'ELASTIC_CLOUD_ID' in env else None
        self.maxsize = get_env_as_int('ELASTIC_MAX_CONN', 25)
        self.http_compress = env.get('ELASTIC_HTTP_COMPRESS', None)
        self.verify_certs = get_env_as_bool('ELASTIC_VERIFY_CERTS', 'off')

        self.host = self.get_host()
        self.http_auth_username = self.env.get('ELASTIC_HTTP_AUTH_USERNAME', 'elastic')
        self.http_auth_password = self.env.get('ELASTIC_HTTP_AUTH_PASSWORD', None)
        self.scheme = self.env.get('ELASTIC_SCHEME', 'http')
        self.query_timeout = get_env_as_int('ELASTIC_QUERY_TIMEOUT', 12)
        self.logging_level = _get_logging_level(
            env['ELASTIC_LOGGING_LEVEL']) if 'ELASTIC_LOGGING_LEVEL' in env else logging.ERROR

        if self.unset_credentials:
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
        self.host = env.get('REDIS_HOST', 'localhost')
        self.port = get_env_as_int('REDIS_PORT', 6379)
        self.redis_host = env.get('REDIS_HOST', 'redis://localhost:6379')
        self.redis_password = env.get('REDIS_PASSWORD', None)

        if self.host.startswith("redis://"):
            self.host = self.host[8:]

        if self.host.startswith("rediss://"):
            self.host = self.host[9:]

        if ":" in self.host:
            self.host = self.host.split(":")[0]

    def get_redis_with_password(self):
        if self.redis_password:
            return self.get_redis_uri(self.redis_host, password=self.redis_password)
        return self.get_redis_uri(self.redis_host)

    @staticmethod
    def get_redis_uri(host, user=None, password=None, protocol="redis", database="0"):
        if not host.startswith('redis://'):
            host = f"{protocol}://{host}"

        if user and password:
            host = f"{protocol}://{user}:{password}@{host[8:]}/{database}"
        elif password:
            host = f"{protocol}://:{password}@{host[8:]}/{database}"

        return host


redis_config = RedisConfig(os.environ)
elastic = ElasticConfig(os.environ)
memory_cache = MemoryCacheConfig(os.environ)


class TracardiConfig(metaclass=Singleton):

    def __init__(self, env):
        self.env = env
        _production = (env['PRODUCTION'].lower() == 'yes') if 'PRODUCTION' in env else False
        self.track_debug = env.get('TRACK_DEBUG', 'no').lower() == 'yes'
        self.save_logs = get_env_as_bool('SAVE_LOGS', 'yes')
        self.enable_event_destinations = get_env_as_bool('ENABLE_EVENT_DESTINATIONS', 'no')
        self.enable_profile_destinations = get_env_as_bool('ENABLE_PROFILE_DESTINATIONS', 'no')
        self.enable_workflow = get_env_as_bool('ENABLE_WORKFLOW', 'yes')
        self.enable_event_validation = get_env_as_bool('ENABLE_EVENT_VALIDATION', 'yes')
        self.enable_event_reshaping = get_env_as_bool('ENABLE_EVENT_RESHAPING', 'yes')
        self.enable_event_source_check = get_env_as_bool('ENABLE_EVENT_SOURCE_CHECK', 'yes')
        self.enable_identification_point = get_env_as_bool('ENABLE_IDENTIFICATION_POINT', 'yes')
        self.system_events = get_env_as_bool('SYSTEM_EVENTS', 'no')
        self.enable_errors_on_response = get_env_as_bool('ENABLE_ERRORS_ON_RESPONSE', 'yes')
        self.enable_field_update_log = get_env_as_bool('ENABLE_FIELD_UPDATE_LOG', 'no')
        self.disallow_bot_traffic = get_env_as_bool('DISALLOW_BOT_TRAFFIC', 'yes')
        self.keep_profile_in_cache_for = get_env_as_int('KEEP_PROFILE_IN_CACHE_FOR', 60*60)
        self.keep_session_in_cache_for = get_env_as_int('KEEP_SESSION_IN_CACHE_FOR', 30 * 60)

        self.skip_errors_on_profile_mapping = get_env_as_bool('SKIP_ERRORS_ON_PROFILE_MAPPING', 'no')

        # Temporary flag
        self.new_collector = get_env_as_bool('NEW_COLLECTOR', 'yes')

        self.profile_cache_ttl = get_env_as_int('PROFILE_CACHE_TTL', 60)
        self.session_cache_ttl = get_env_as_int('SESSION_CACHE_TTL', 60)

        # Not used now
        self.sync_profile_tracks_max_repeats = get_env_as_int('SYNC_PROFILE_TRACKS_MAX_REPEATS', 10)
        self.sync_profile_tracks_wait = get_env_as_int('SYNC_PROFILE_TRACKS_WAIT', 1)
        self.storage_driver = env.get('STORAGE_DRIVER', 'elastic')
        self.tracardi_pro_host = env.get('TRACARDI_PRO_HOST', 'pro.tracardi.com')
        self.tracardi_pro_port = get_env_as_int('TRACARDI_PRO_PORT', 40000)
        self.logging_level = _get_logging_level(env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in env else logging.WARNING
        self.server_logging_level = _get_logging_level(
            env['SERVER_LOGGING_LEVEL']) if 'SERVER_LOGGING_LEVEL' in env else logging.WARNING
        self.multi_tenant = get_env_as_bool('MULTI_TENANT', "no")
        self.multi_tenant_manager_url = env.get('MULTI_TENANT_MANAGER_URL', None)
        self.multi_tenant_manager_api_key = env.get('MULTI_TENANT_MANAGER_API_KEY', None)
        self.expose_gui_api = get_env_as_bool('EXPOSE_GUI_API', 'yes')
        self.version: Version = Version(version=VERSION, name=TENANT_NAME, production=_production)
        self.image_tag = env.get('IMAGE_TAG', 'n/a')
        self.installation_token = env.get('INSTALLATION_TOKEN', 'tracardi')
        random_hash = md5(f"akkdskjd-askmdj-jdff-3039djn-{self.version.db_version}".encode()).hexdigest()
        self.internal_source = f"@internal-{random_hash[:20]}"
        self.segmentation_source = f"@segmentation-{random_hash[:20]}"
        self.demo_source = f"@demo-{random_hash[:20]}"

        self.event_partitioning = env.get('EVENT_PARTITIONING', 'quarter')
        self.profile_partitioning = env.get('PROFILE_PARTITIONING', 'quarter')
        self.session_partitioning = env.get('SESSION_PARTITIONING', 'quarter')
        self.entity_partitioning = env.get('ITEM_PARTITIONING', 'quarter')
        self.item_partitioning = env.get('ITEM_PARTITIONING', 'year')
        self.log_partitioning = env.get('LOG_PARTITIONING', 'month')
        self.dispatch_log_partitioning = env.get('DISPATCH_LOG_PARTITIONING', 'month')
        self.console_log_partitioning = env.get('CONSOLE_LOG_PARTITIONING', 'month')
        self.user_log_partitioning = env.get('USER_LOG_PARTITIONING', 'year')
        self.field_change_log_partitioning = env.get('FIELD_CHANGE_LOG_PARTITIONING', 'month')
        self.auto_profile_merging = env.get('AUTO_PROFILE_MERGING', 's>a.d-kljsa87^5adh')
        self.apm_on = get_env_as_bool('APM', 'yes')

        self._config = None
        self._unset_secrets()

        if self.multi_tenant_manager_url:
            self.multi_tenant_manager_url = self.multi_tenant_manager_url.strip("/")

        if self.multi_tenant and (self.multi_tenant_manager_url is None or self.multi_tenant_manager_api_key is None):
            if self.multi_tenant_manager_url is None:
                logger.warning('No MULTI_TENANT_MANAGER_URL set for MULTI_TENANT mode. Either set '
                               'the MULTI_TENANT_MANAGER_URL or set MULTI_TENANT to "no"',
                               extra=ExtraInfo.build(object=self, origin="configuration", error_number="C0001")
                               )

            if self.multi_tenant_manager_api_key is None:
                logger.warning('No MULTI_TENANT_MANAGER_API_KEY set for MULTI_TENANT mode. Either set '
                               'the MULTI_TENANT_MANAGER_API_KEY or set MULTI_TENANT to "no"',
                               extra=ExtraInfo.build(object=self, origin="configuration", error_number="C0002")
                               )

        if self.multi_tenant and not is_valid_url(self.multi_tenant_manager_url):
            logger.warning('Env MULTI_TENANT_MANAGER_URL is not valid URL.',
                           extra=ExtraInfo.build(object=self, origin="configuration", error_number="C0003")
                           )

        if self.apm_on and self.auto_profile_merging and len(self.auto_profile_merging) < 20:
            logger.warning(
                'Security risk. Env AUTO_PROFILE_MERGING is too short. It must be at least 20 chars long.',
                extra=ExtraInfo.build(object=self, origin="configuration", error_number="C0004")
            )

    def is_apm_on(self) -> bool:
        return self.apm_on


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

class ServerConfig:
    def __init__(self, env):
        self.page_size = int(env['AUTOLOAD_PAGE_SIZE']) if 'AUTOLOAD_PAGE_SIZE' in env else 25
        self.x_forwarded_ip_header = env.get('USE_X_FORWARDED_IP', None)
        self.api_docs = (env['API_DOCS'].lower() == "yes") if 'API_DOCS' in env else True
        self.performance_tracking = env.get('PERFORMANCE_TRACKING', None)


server = ServerConfig(os.environ)
tracardi = TracardiConfig(os.environ)
mysql = MysqlConfig(os.environ)
starrocks = StarRocksConfig(os.environ)