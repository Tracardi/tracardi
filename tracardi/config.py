import logging
import os
from hashlib import md5

import yaml

from tracardi.domain.version import Version
from tracardi.domain.yaml_config import YamlConfig
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.logging.tools import _get_logging_level
from tracardi.service.singleton import Singleton
from tracardi.service.utils.environment import get_env_as_int
from tracardi.service.utils.validators import is_valid_url

VERSION = os.environ.get('_DEBUG_VERSION', '0.9.0-rc1')
TENANT_NAME = os.environ.get('TENANT_NAME', None)

logger = get_logger(__name__)

class MemoryCacheConfig:
    def __init__(self, env):
        self.event_to_profile_coping_ttl = get_env_as_int('EVENT_TO_PROFILE_COPY_CACHE_TTL', 2)
        self.source_ttl = get_env_as_int('SOURCE_CACHE_TTL', 2)
        self.session_cache_ttl = get_env_as_int('SESSION_CACHE_TTL', 2)
        self.event_validation_cache_ttl = get_env_as_int('EVENT_VALIDATION_CACHE_TTL', 2)
        self.event_metadata_cache_ttl = get_env_as_int('EVENT_METADATA_CACHE_TTL', 2)
        self.event_destination_cache_ttl = get_env_as_int('EVENT_DESTINATION_CACHE_TTL', 2)
        self.profile_destination_cache_ttl = get_env_as_int('PROFILE_DESTINATION_CACHE_TTL', 2)
        self.data_compliance_cache_ttl = get_env_as_int('DATA_COMPLIANCE_CACHE_TTL', 2)
        self.trigger_rule_cache_ttl = get_env_as_int('TRIGGER_RULE_CACHE_TTL', 5)


class MysqlConfig:

    def __init__(self, env):
        self.env = env
        self.mysql_database_uri = env.get('MYSQL_DATABASE_URI', "mysql+aiomysql://root:root@localhost/")
        self.mysql_database = env.get('MYSQL_DATABASE', "tracardi")
        self.mysql_echo = env.get('MYSQL_ECHO', "no") == "yes"

        self.mysql_database_uri = self.mysql_database_uri.strip(" /")
        self.mysql_database = self.mysql_database.strip(" /")


class ElasticConfig:

    def __init__(self, env):
        self.env = env
        self.unset_credentials = env.get('UNSET_CREDENTIALS', "no") == 'yes'
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
        self.verify_certs = (env['ELASTIC_VERIFY_CERTS'].lower() == 'yes') if 'ELASTIC_VERIFY_CERTS' in env else None

        self.refresh_profiles_after_save = env.get('ELASTIC_REFRESH_PROFILES_AFTER_SAVE', 'no').lower() == 'yes'

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
        self.port = get_env_as_int('REDIS_PORT', '6379')
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
        self.save_logs = env.get('SAVE_LOGS', 'yes').lower() == 'yes'
        self.enable_event_destinations = env.get('ENABLE_EVENT_DESTINATIONS', 'no').lower() == 'yes'
        self.enable_profile_destinations = env.get('ENABLE_PROFILE_DESTINATIONS', 'no').lower() == 'yes'
        self.enable_segmentation_wf_triggers = env.get('ENABLE_SEGMENTATION_WF_TRIGGERS', 'no').lower() == 'yes'
        self.enable_workflow = env.get('ENABLE_WORKFLOW', 'yes').lower() == 'yes'
        self.enable_event_validation = env.get('ENABLE_EVENT_VALIDATION', 'yes').lower() == 'yes'
        self.enable_event_reshaping = env.get('ENABLE_EVENT_RESHAPING', 'yes').lower() == 'yes'
        self.enable_event_source_check = env.get('ENABLE_EVENT_SOURCE_CHECK', 'yes').lower() == 'yes'
        self.enable_profile_immediate_flush = env.get('ENABLE_PROFILE_IMMEDIATE_FLUSH', 'yes').lower() == 'yes'
        self.enable_identification_point = env.get('ENABLE_IDENTIFICATION_POINT', 'yes').lower() == 'yes'
        self.enable_post_event_segmentation = env.get('ENABLE_POST_EVENT_SEGMENTATION', 'yes').lower() == 'yes'
        self.system_events = env.get('SYSTEM_EVENTS', 'yes').lower() == 'yes'
        self.enable_errors_on_response = env.get('ENABLE_ERRORS_ON_RESPONSE', 'yes').lower() == 'yes'
        self.enable_field_update_log = env.get('ENABLE_FIELD_UPDATE_LOG', 'yes').lower() == 'yes'
        self.allow_bot_traffic = env.get('ALLOW_BOT_TRAFFIC', 'no').lower() == 'yes'
        self.keep_profile_in_cache_for = get_env_as_int('KEEP_PROFILE_IN_CACHE_FOR', 60*60)
        self.keep_session_in_cache_for = get_env_as_int('KEEP_SESSION_IN_CACHE_FOR', 30 * 60)

        self.skip_errors_on_profile_mapping = env.get('SKIP_ERRORS_ON_PROFILE_MAPPING', 'no').lower() == 'yes'

        # Temporary flag
        self.new_collector = env.get('NEW_COLLECTOR', 'yes').lower() == 'yes'

        self.profile_cache_ttl = get_env_as_int('PROFILE_CACHE_TTL', 60)
        self.session_cache_ttl = get_env_as_int('SESSION_CACHE_TTL', 60)

        # Not used now
        self.sync_profile_tracks_max_repeats = get_env_as_int('SYNC_PROFILE_TRACKS_MAX_REPEATS', 10)
        self.sync_profile_tracks_wait = get_env_as_int('SYNC_PROFILE_TRACKS_WAIT', 1)
        self.storage_driver = env.get('STORAGE_DRIVER', 'elastic')
        self.tracardi_pro_host = env.get('TRACARDI_PRO_HOST', 'pro.tracardi.com')
        self.tracardi_pro_port = get_env_as_int('TRACARDI_PRO_PORT', 40000)
        self.tracardi_scheduler_host = env.get('TRACARDI_SCHEDULER_HOST', 'scheduler.tracardi.com')
        self.logging_level = _get_logging_level(env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in env else logging.WARNING
        self.server_logging_level = _get_logging_level(
            env['SERVER_LOGGING_LEVEL']) if 'SERVER_LOGGING_LEVEL' in env else logging.WARNING
        self.multi_tenant = env.get('MULTI_TENANT', "no") == 'yes'
        self.multi_tenant_manager_url = env.get('MULTI_TENANT_MANAGER_URL', None)
        self.multi_tenant_manager_api_key = env.get('MULTI_TENANT_MANAGER_API_KEY', None)
        self.expose_gui_api = env.get('EXPOSE_GUI_API', 'yes').lower() == "yes"
        self.version: Version = Version(version=VERSION, name=TENANT_NAME, production=_production)
        self.installation_token = env.get('INSTALLATION_TOKEN', 'tracardi')
        random_hash = md5(f"akkdskjd-askmdj-jdff-3039djn-{self.version.db_version}".encode()).hexdigest()
        self.internal_source = f"@internal-{random_hash[:20]}"
        self.segmentation_source = f"@segmentation-{random_hash[:20]}"
        self.demo_source = f"@demo-{random_hash[:20]}"

        self.event_partitioning = env.get('EVENT_PARTITIONING', 'second')
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
        self.apm_on = env.get('APM', 'yes') == 'yes'

        self._config = None
        self._unset_secrets()

        if self.multi_tenant and (self.multi_tenant_manager_url is None or self.multi_tenant_manager_api_key is None):
            if self.multi_tenant_manager_url is None:
                logger.warning('No MULTI_TENANT_MANAGER_URL set for MULTI_TENANT mode. Either set '
                               'the MULTI_TENANT_MANAGER_URL or set MULTI_TENANT to "no"')

            if self.multi_tenant_manager_api_key is None:
                logger.warning('No MULTI_TENANT_MANAGER_API_KEY set for MULTI_TENANT mode. Either set '
                               'the MULTI_TENANT_MANAGER_API_KEY or set MULTI_TENANT to "no"')

        if self.multi_tenant and not is_valid_url(self.multi_tenant_manager_url):
            logger.warning('Env MULTI_TENANT_MANAGER_URL is not valid URL.')

        if self.apm_on and self.auto_profile_merging and len(self.auto_profile_merging) < 20:
            logger.warning('Security risk. Env AUTO_PROFILE_MERGING is too short. It must be at least 20 chars long.')

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


tracardi = TracardiConfig(os.environ)
mysql = MysqlConfig(os.environ)
