from tracardi.config import elastic, tracardi, mysql, memory_cache, redis_config, server
from tracardi.domain.settings import SystemSettings
from tracardi.service.license import License

if License.has_license():
    from com_tracardi.service.settings import com_system_settings

system_settings = [
    SystemSettings(
        **{
            "label": "API_DOCS",
            "value": server.api_docs,
            "desc": "Default: Yes. Turns off APi documentations at /docs."
        }
    ),
    SystemSettings(
        **{
            "label": "SYSTEM_EVENTS",
            "value": tracardi.system_events,
            "desc": "Default: Yes. Register system events like: profile-created, session-opened, etc."
        }
    ),
    SystemSettings(
        **{
            "label": "MULTI_TENANT",
            "value": tracardi.multi_tenant,
            "desc": "Default: No. Turns on multi tenancy feature for commercial versions."
        }
    ),
    SystemSettings(
        **{
            "label": "AUTOLOAD_PAGE_SIZE",
            "value": server.page_size,
            "desc": "The size of automatically loaded page, defaults"
                    " to 25."
        }
    ),
    SystemSettings(
        **{
            "label": "EXPOSE_GUI_API",
            "value": tracardi.expose_gui_api,
            "desc": "Expose GUI API or not, defaults to True, "
                    "can be changed by setting to 'yes' (then it's True) or 'no', "
                    "which makes it False."
        }
    ),
    SystemSettings(
        **{
            "label": "TRACK_DEBUG",
            "value": tracardi.track_debug,
            "desc": "Track debug or not, defaults to False."
        }
    ),
    SystemSettings(
        **{
            "label": "TRACARDI_PRO_HOST",
            "value": tracardi.tracardi_pro_host,
            "desc": "Defines the Tracardi Pro Services Host."
        }
    ),
    SystemSettings(
        **{
            "label": "TRACARDI_PRO_PORT",
            "value": tracardi.tracardi_pro_port,
            "desc": "Defines the Tracardi Pro Services Port."
        }
    ),
    SystemSettings(
        **{
            "label": "TRACARDI_SCHEDULER_HOST",
            "value": tracardi.tracardi_scheduler_host,
            "desc": "Defines the Tracardi Pro Scheduler Host."
        }
    ),
    SystemSettings(
        **{
            "label": "EVENT_TO_PROFILE_COPY_CACHE_TTL",
            "value": memory_cache.event_to_profile_coping_ttl,
            "desc": "Default: 2. Set caching time for the event to profile schema. Set 0 for no caching."
        }
    ),
    SystemSettings(
        **{
            "label": "SOURCE_CACHE_TTL",
            "value": memory_cache.source_ttl,
            "desc": "Default: 2. Each resource read is cached for given seconds. That means that when you change any "
                    "resource data, e.g. credentials it wil be available with max 2 seconds."
        }
    ),
    SystemSettings(
        **{
            "label": "SESSION_CACHE_TTL",
            "value": memory_cache.session_cache_ttl,
            "desc": "Default: 2. Set session caching time. Set 0 for no caching."
        }
    ),
    SystemSettings(
        **{
            "label": "EVENT_VALIDATION_CACHE_TTL",
            "value": memory_cache.event_validation_cache_ttl,
            "desc": "Default: 2. Set event validation schema caching time. Set 0 for no caching."
        }
    ),
    SystemSettings(
        **{
            "label": "TRIGGER_RULE_CACHE_TTL",
            "value": memory_cache.trigger_rule_cache_ttl,
            "desc": "Default: 5. Set cache time for workflow triggers. Set 0 for no caching."
        }
    ),
    SystemSettings(
        **{
            "label": "DATA_COMPLIANCE_CACHE_TTL",
            "value": memory_cache.data_compliance_cache_ttl,
            "desc": "Default: 2. Set cache time for data compliance rules Set 0 for no caching."
        }
    ),

    SystemSettings(
        **{
            "label": "EVENT_METADATA_CACHE_TTL",
            "value": memory_cache.event_metadata_cache_ttl,
            "desc": "Default: 2. Set cache time for event tagging, indexing, etc. configuration. Set 0 for no caching."
        }
    ),
    SystemSettings(
        **{
            "label": "SYNC_PROFILE_TRACKS_MAX_REPEATS",
            "value": tracardi.sync_profile_tracks_max_repeats,
            "desc": "Maximum number of repeated requests the must be synchronized. If this number is crossed then "
                    "the requests will not be synchronized. Do not set it to big number as this can block server. "
                    "Default: 10"
        }
    ),
    SystemSettings(
        **{
            "label": "SYNC_PROFILE_TRACKS_WAIT",
            "value": tracardi.sync_profile_tracks_wait,
            "desc": "Maximum number of seconds to wait between profile synchronization attempts. Profile must be saved "
                    "before the next rule can be run  on it. Default: 1"
        }
    ),
    SystemSettings(
        **{
            "label": "MYSQL_HOST",
            "value": mysql.mysql_host,
            "desc": "Mysql host."
        }
    ),
    SystemSettings(
        **{
            "label": "MYSQL_DATABASE",
            "value": mysql.mysql_database,
            "desc": "Default: tracardi, Mysql database."
        }
    ),
    SystemSettings(
        **{
            "label": "MYSQL_PORT",
            "value": mysql.mysql_port,
            "desc": "Default: 3306, Mysql port."
        }
    ),
    SystemSettings(
        **{
            "label": "MYSQL_SCHEMA",
            "value": mysql.mysql_schema,
            "desc": "Default: mysql+aiomysql://, Mysql schema."
        }
    ),
    SystemSettings(
        **{
            "label": "MYSQL_SCHEMA_SYNC",
            "value": mysql.mysql_schema_sync,
            "desc": "Default: mysql+pymysql://, Mysql sync schema."
        }
    ),
    SystemSettings(
        **{
            "label": "LOGGING_LEVEL",
            "value": tracardi.logging_level,
            "desc": "The logging level. Defaults to logging.WARNING."
        }
    ),
    SystemSettings(
        **{
            "label": "PRODUCTION",
            "value": tracardi.version.production,
            "desc": "This variable defines default API context. If it is set to \"production,\" "
                    "the data will be accessible within the production GUI context."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_HOST",
            "value": elastic.host,
            "desc": "Default: 127.0.0.1. This setting defines a IP address of elastic search instance. See Connecting "
                    "to elastic cluster for more information how to connect to a cluster of servers."
        }
    ),
    SystemSettings(
        **{
            "label": "EVENT_PARTITIONING",
            "value": tracardi.event_partitioning,
            "desc": "Default: month. Determines how often event data is partitioned."
        }
    ),
    SystemSettings(
        **{
            "label": "PROFILE_PARTITIONING",
            "value": tracardi.profile_partitioning,
            "desc": "Default: quarter. Sets the partitioning interval for user profile data."
        }
    ),
    SystemSettings(
        **{
            "label": "SESSION_PARTITIONING",
            "value": tracardi.session_partitioning,
            "desc": "Default: quarter. Defines the frequency of session data partitioning."
        }
    ),
    SystemSettings(
        **{
            "label": "ENTITY_PARTITIONING",
            "value": tracardi.entity_partitioning,
            "desc": "Default: quarter. Specifies the partitioning schedule for entity data."
        }
    ),
    SystemSettings(
        **{
            "label": "ITEM_PARTITIONING",
            "value": tracardi.item_partitioning,
            "desc": "Default: year. Determines the partitioning interval for items."
        }
    ),
    SystemSettings(
        **{
            "label": "LOG_PARTITIONING",
            "value": tracardi.log_partitioning,
            "desc": "Default: month. Log data partitioning frequency."
        }
    ),
    SystemSettings(
        **{
            "label": "DISPATCH_LOG_PARTITIONING",
            "value": tracardi.dispatch_log_partitioning,
            "desc": "Default: month. Sets how often dispatch logs are partitioned."
        }
    ),
    SystemSettings(
        **{
            "label": "CONSOLE_LOG_PARTITIONING",
            "value": tracardi.console_log_partitioning,
            "desc": "Default: month. Interval for partitioning console log data."
        }
    ),
    SystemSettings(
        **{
            "label": "USER_LOG_PARTITIONING",
            "value": tracardi.user_log_partitioning,
            "desc": "Default: year. Frequency of user log data partitioning."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_INDEX_SHARDS",
            "value": elastic.shards,
            "desc": "Default: 5. Number of shards per index."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_INDEX_REPLICAS",
            "value": elastic.replicas,
            "desc": "Default: 5. Number of replicas of index."
        }
    ),
    SystemSettings(
        **{
            "label": "TENANT_NAME",
            "value": tracardi.version.name,
            "desc": "Default: None. This setting defines a prefix for all tracardi indices."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_SNIFF_ON_START",
            "value": elastic.sniff_on_start,
            "desc": "Default: None. When you enable this option, the client will attempt to execute an Elasticsearch "
                    "sniff request during the client initialization or first usage. Search documentation for "
                    "sniffing to get more information."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_SNIFF_ON_CONNECTION_FAIL",
            "value": elastic.sniff_on_connection_fail,
            "desc": "Default: None. If you enable this option, the client will attempt to execute a sniff request every"
                    " time a node is faulty, which means a broken connection or a dead node."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_SNIFFER_TIMEOUT",
            "value": elastic.sniffer_timeout,
            "desc": "Default: None, Time out for sniff operation."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_HTTP_AUTH_USERNAME",
            "value": elastic.has('http_auth_username'),
            "desc": "Default: None. Elastic search username. Search for elastic authentication "
                    "for more information on how to configure connection to elastic."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_HTTP_AUTH_PASSWORD",
            "value": elastic.has('http_auth_password'),
            "desc": "Default: None. Elastic search password. Search for elastic authentication "
                    "for more information on how to configure connection to elastic."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_SCHEME",
            "value": elastic.scheme,
            "desc": "Default: http. Available options http, https."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_CA_FILE",
            "value": elastic.ca_file,
            "desc": "Default: None. Elastic CA file. Search for elastic authentication for more information on how "
                    "to configure connection to elastic."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_API_KEY",
            "value": elastic.api_key,
            "desc": "Default: None. Elastic API key. Search for elastic authentication for more information on how "
                    "to configure connection to elastic."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_CLOUD_ID",
            "value": elastic.cloud_id,
            "desc": "Default: None. Search for elastic authentication for more information on how to configure "
                    "connection to elastic."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_MAX_CONN",
            "value": elastic.maxsize,
            "desc": "Default: None. Defines max connection to elastic cluster. It defaults to elastic default value."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_QUERY_TIMEOUT",
            "value": elastic.query_timeout,
            "desc": "Default: 12. Defines max connection timeout."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_HTTP_COMPRESS",
            "value": elastic.http_compress,
            "desc": "default value: None. Set compression on data when the client calls the server."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_VERIFY_CERTS",
            "value": elastic.verify_certs,
            "desc": "default value: None. Verify certificates when https schema is set. Set it to no if certificates "
                    "has no CA."
        }
    ),
    SystemSettings(
        **{
            "label": "ELASTIC_LOGGING_LEVEL",
            "value": elastic.logging_level,
            "desc": "Default WARNING. Sets logging level of elastic requests. It may be useful to set it to INFO when"
                    " debugging Tracardi."
        }
    ),
    SystemSettings(
        **{
            "label": "REDIS_HOST",
            "value": redis_config.redis_host,
            "desc": "Default: redis://localhost:6379. This setting is used only when SYNC_PROFILE_TRACKS is equal to "
                    "yes. This is the host URI of Redis instance that is required to synchronize profile tracks. "
                    "Available only in commercial version of Tracardi."
        }
    ),
    SystemSettings(
        **{
            "label": "REDIS_PASSWORD",
            "value": "Set" if redis_config.redis_password is not None else "Unset",
            "desc": "Default: None. This is Redis password."
        }
    ),
    SystemSettings(
        **{
            "label": "SAVE_LOGS",
            "value": tracardi.save_logs,
            "desc": "Default: yes. When set to yes all logs will be saved in tracardi log."
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_WORKFLOW",
            "value": tracardi.enable_workflow,
            "desc": "Default: yes. Enables processing events by workflows.",
            "expose": True
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_EVENT_DESTINATIONS",
            "value": tracardi.enable_event_destinations,
            "desc": "Default: no. Enables dispatching events to destinations.",
            "expose": True
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_PROFILE_DESTINATIONS",
            "value": tracardi.enable_profile_destinations,
            "desc": "Default: no. Enables dispatching profiles to destinations.",
            "expose": True
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_EVENT_RESHAPING",
            "value": tracardi.enable_event_reshaping,
            "desc": "Default: yes. Enables event reshaping.",
            "expose": True
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_EVENT_VALIDATION",
            "value": tracardi.enable_event_validation,
            "desc": "Default: yes. Enables event validation.",
            "expose": True
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_FIELD_UPDATE_LOG",
            "value": tracardi.enable_field_update_log,
            "desc": "Default: Yes. Save timestamps of updated fields."
        }
    ),
    SystemSettings(
        **{
            "label": "ENABLE_ERRORS_ON_RESPONSE",
            "value": tracardi.enable_errors_on_response,
            "desc": "Default: Yes. Display errors on track response."
        }
    ),
    SystemSettings(
        **{
            "label": "AUTO_PROFILE_MERGING",
            "value": tracardi.is_apm_on(),
            "desc": "Default: tracardi. Merge profile automatically on change of defined profile fields. AUTO_PROFILE_MERGING value is used to salt the profile merging keys hashing. Set value to random value, min 20 letters.",
            "expose": True
        }
    ),
    SystemSettings(
        **{
            "label": "DISALLOW_BOT_TRAFFIC",
            "value": tracardi.disallow_bot_traffic,
            "desc": "Default: Yes. If set to Yes then block bot traffic."
        }
    ),
    SystemSettings(
        **{
            "label": "KEEP_PROFILE_IN_CACHE_FOR",
            "value": tracardi.keep_profile_in_cache_for,
            "desc": "Default: 3600. How many seconds should the profile be kept in cache."
        }
    ),
    SystemSettings(
        **{
            "label": "KEEP_SESSION_IN_CACHE_FOR",
            "value": tracardi.keep_session_in_cache_for,
            "desc": "Default: 1800. How many seconds should the session be kept in cache."
        }
    ),
]

def get_system_envs():

    _system_settings = system_settings
    if License.has_license():
        _system_settings += com_system_settings

    return {item.label: item.value for item in _system_settings if item.expose}


def list_system_envs():

    if License.has_license():
        return system_settings + com_system_settings

    return system_settings