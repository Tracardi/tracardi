from sqlalchemy import Index, Float

from sqlalchemy import (Column, String, DateTime, Boolean, JSON,
                        ForeignKey, PrimaryKeyConstraint, Text, Integer, UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BridgeTable(Base):
    __tablename__ = 'bridge'

    id = Column(String(40), unique=True)
    tenant = Column(String(40))
    name = Column(String(64), index=True)
    description = Column(Text)
    type = Column(String(48))
    config = Column(JSON)
    form = Column(JSON)
    manual = Column('manual', Text, nullable=True, quote=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant'),
    )


class EventSourceTable(Base):
    __tablename__ = 'event_source'

    id = Column(String(40), unique=True)
    tenant = Column(String(40))
    production = Column(Boolean)
    timestamp = Column(DateTime)
    update = Column(DateTime)
    type = Column(String(32))
    bridge_id = Column(String(40), ForeignKey('bridge.id'))
    bridge_name = Column(String(128))
    name = Column(String(64), index=True)
    description = Column(String(255))
    channel = Column(String(32))
    url = Column(String(255))
    enabled = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    transitional = Column(Boolean, default=False)
    tags = Column(String(255))
    groups = Column(String(255))
    icon = Column(String(32))
    config = Column(JSON)
    configurable = Column(Boolean)
    hash = Column(String(255))
    returns_profile = Column(Boolean)
    permanent_profile_id = Column(Boolean, default=False)
    requires_consent = Column(Boolean, default=False)
    synchronize_profiles = Column(Boolean)
    manual = Column('manual', Text, quote=True)
    endpoints_get_url = Column(String(255))
    endpoints_get_method = Column(String(255))
    endpoints_post_url = Column(String(255))
    endpoints_post_method = Column(String(255))

    bridge = relationship("BridgeTable")

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False


class WorkflowTable(Base):
    __tablename__ = 'workflow'

    id = Column(String(40))
    timestamp = Column(DateTime)
    deploy_timestamp = Column(DateTime)
    name = Column(String(64), index=True)
    description = Column(String(255))
    type = Column(String(64), default="collection", index=True)
    tags = Column(String(255))

    draft = Column(JSON)

    file_name = Column(String(64))

    lock = Column(Boolean)
    deployed = Column(Boolean, default=False)
    debug_enabled = Column(Boolean, default=False)
    debug_logging_level = Column(String(32))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False


class WorkflowTriggerTable(Base):
    __tablename__ = 'workflow_trigger'

    id = Column(String(40))
    name = Column(String(150), index=True)
    description = Column(String(255))
    type = Column(String(64))
    metadata_time_insert = Column(DateTime)
    event_type_id = Column(String(40))
    event_type_name = Column(String(64))
    flow_id = Column(String(40), index=True)
    flow_name = Column(String(64))
    segment_id = Column(String(40), index=True)
    segment_name = Column(String(64))
    source_id = Column(String(40), index=True)
    source_name = Column(String(64))
    properties = Column(JSON)
    enabled = Column(Boolean, default=False)
    tags = Column(String(255), index=True)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_collector', 'event_type_id', 'source_id', 'enabled', 'tenant', 'production'),
    )

    running: bool = False


class ResourceTable(Base):
    __tablename__ = 'resource'

    id = Column(String(40))
    tenant = Column(String(40))
    production = Column(Boolean)
    type = Column(String(48))
    timestamp = Column(DateTime)
    name = Column(String(64), index=True)
    description = Column(String(255))
    credentials = Column(Text)
    enabled = Column(Boolean, default=False)
    tags = Column(String(255), index=True)
    groups = Column(String(255))
    icon = Column(String(255))
    destination = Column(String(255))

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False


class PluginTable(Base):
    __tablename__ = 'plugin'

    id = Column(String(64))
    tenant = Column(String(40))

    metadata_time_insert = Column(DateTime)
    metadata_time_update = Column(DateTime, nullable=True)
    metadata_time_create = Column(DateTime, nullable=True)
    plugin_debug = Column(Boolean)
    plugin_metadata_desc = Column(String(255))
    plugin_metadata_brand = Column(String(32))
    plugin_metadata_group = Column(String(32))
    plugin_metadata_height = Column(Integer)
    plugin_metadata_width = Column(Integer)
    plugin_metadata_icon = Column(String(32))
    plugin_metadata_keywords = Column(String(255))
    plugin_metadata_name = Column(String(64))
    plugin_metadata_type = Column(String(24))
    plugin_metadata_tags = Column(String(128))
    plugin_metadata_pro = Column(Boolean)
    plugin_metadata_commercial = Column(Boolean)
    plugin_metadata_remote = Column(Boolean)
    plugin_metadata_documentation = Column(JSON)
    plugin_metadata_frontend = Column(Boolean)
    plugin_metadata_emits_event = Column(JSON)
    plugin_metadata_purpose = Column(String(64))
    plugin_spec_id = Column(String(64))
    plugin_spec_class_name = Column(String(255))
    plugin_spec_module = Column(String(128))
    plugin_spec_inputs = Column(String(255))
    plugin_spec_outputs = Column(String(255))
    plugin_spec_microservice = Column(JSON)
    plugin_spec_init = Column(JSON)
    plugin_spec_skip = Column(Boolean)
    plugin_spec_block_flow = Column(Boolean)
    plugin_spec_run_in_background = Column(Boolean)
    plugin_spec_on_error_continue = Column(Boolean)
    plugin_spec_on_connection_error_repeat = Column(Integer)
    plugin_spec_append_input_payload = Column(Boolean)
    plugin_spec_join_input_payload = Column(Boolean)
    plugin_spec_form = Column(JSON)
    plugin_spec_manual = Column(String(64))
    plugin_spec_author = Column(String(64))
    plugin_spec_license = Column(String(32))
    plugin_spec_version = Column(String(32))
    plugin_spec_run_once_value = Column(String(64))
    plugin_spec_run_once_ttl = Column(Integer)
    plugin_spec_run_once_type = Column(String(64))
    plugin_spec_run_once_enabled = Column(Boolean, default=False)
    plugin_spec_node_on_remove = Column(String(128))
    plugin_spec_node_on_create = Column(String(128))
    plugin_start = Column(Boolean)
    settings_enabled = Column(Boolean, default=False)
    settings_hidden = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant'),
    )


class DestinationTable(Base):
    __tablename__ = 'destination'

    id = Column(String(40))
    name = Column(String(128), index=True)

    description = Column(Text)
    destination = Column(JSON)
    condition = Column(Text)
    mapping = Column(JSON)
    enabled = Column(Boolean, default=False)
    on_profile_change_only = Column(Boolean)
    event_type_id = Column(String(40))
    event_type_name = Column(String(128))
    source_id = Column(String(40))
    source_name = Column(String(128))
    resource_id = Column(String(40), index=True)
    tags = Column(String(255))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_collector', 'event_type_id', 'source_id', 'enabled', 'tenant', 'production'),

    )

    running: bool = False


class VersionTable(Base):
    __tablename__ = 'version'

    es_schema_version = Column(String(64))
    api_version = Column(String(64))
    mysql_schema_version = Column(String(64))

    tenant = Column(String(40))

    __table_args__ = (
        PrimaryKeyConstraint('tenant', 'api_version'),
    )


class UserTable(Base):
    __tablename__ = 'user'

    id = Column(String(40))
    password = Column(String(128))
    name = Column(String(128))
    email = Column(String(128), index=True)
    roles = Column(String(255))
    enabled = Column(Boolean)
    expiration_timestamp = Column(Integer)
    preference = Column(JSON)

    tenant = Column(String(40))

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'email'),
        UniqueConstraint('tenant', 'email', 'password', name='uiq_email_password')
    )


Index('index_email_password', UserTable.email, UserTable.password)


class IdentificationPointTable(Base):
    __tablename__ = 'identification_point'

    id = Column(String(40))
    name = Column(String(255))
    description = Column(Text)
    source_id = Column(String(40), index=True)
    source_name = Column(String(128))
    event_type_id = Column(String(40))
    event_type_name = Column(String(128))
    fields = Column(JSON)
    enabled = Column(Boolean, default=False)
    settings = Column(JSON)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_collector', 'tenant', 'production', 'enabled', 'event_type_id', 'source_id')
    )

    running: bool = False


class TracardiProTable(Base):
    __tablename__ = 'tracardi_pro'

    id = Column(String(40))
    token = Column(String(255))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )


class EventRedirectTable(Base):
    __tablename__ = 'event_redirect'

    id = Column(String(40))
    name = Column(String(128))
    description = Column(Text)
    url = Column(String(128))
    source_id = Column(String(40))
    source_name = Column(String(128))
    event_type = Column(String(64))
    props = Column(JSON)
    tags = Column(String(128))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_collector', 'event_type', 'source_id', 'tenant', 'production'),
    )

    running: bool = False


class EventValidationTable(Base):
    __tablename__ = 'event_validation'

    id = Column(String(40))
    name = Column(String(128))
    description = Column(Text)
    validation = Column(JSON)
    tags = Column(String(128))
    event_type = Column(String(64))
    enabled = Column(Boolean, default=False)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_collector', 'event_type', 'enabled', 'tenant', 'production'),
    )

    running: bool = False


class ConsentTypeTable(Base):
    __tablename__ = 'consent_type'

    id = Column(String(40))
    name = Column(String(128))
    description = Column(Text)
    revokable = Column(Boolean)
    default_value = Column(String(255))
    enabled = Column(Boolean, default=False)
    tags = Column(String(128))
    required = Column(Boolean)
    auto_revoke = Column(String(128))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False


class EventReshapingTable(Base):
    __tablename__ = 'event_reshaping'

    id = Column(String(40))
    name = Column(String(128))
    description = Column(Text)
    reshaping = Column(JSON)
    tags = Column(String(128))
    event_type = Column(String(64))
    event_source_id = Column(String(40))
    event_source_name = Column(String(128))
    enabled = Column(Boolean, default=False)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_collector', 'event_type', 'tenant', 'production', 'enabled')
    )

    running: bool = False


class EventMappingTable(Base):
    __tablename__ = 'event_mapping'

    id = Column(String(40), index=True)
    name = Column(String(128))
    description = Column(Text)
    event_type = Column(String(64), index=True, unique=True)
    tags = Column(String(128))
    journey = Column(String(64))
    enabled = Column(Boolean, default=False)
    index_schema = Column(JSON)

    # Additional fields for multi-tenancy
    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        UniqueConstraint('event_type', name='uiq_event_type'),
        Index('idx_collector', 'event_type', 'tenant', 'production', 'enabled')
    )

    running: bool = False


# TODO check if not used
class EventPropertiesTable(Base):
    __tablename__ = 'event_properties'

    id = Column(String(40), index=True, unique=True)
    event_type = Column(String(40), ForeignKey('event_mapping.event_type'), unique=True)  # sign-in
    field_path = Column(String(255), index=True, unique=True)  # properties.email
    field_type = Column(String(40))  # string
    traits_field = Column(String(255), nullable=True)  # event_to_traits

    # Additional fields for multi-tenancy
    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('ix_event_type_fields', 'event_type', 'field_path'),
        UniqueConstraint('event_type', 'field_path', name='uiq_event_type')
    )

    running: bool = False


# TODO check if not used
class EventPropertiesToEntityMappingTable(Base):
    __tablename__ = 'event_properties_to_entity_mapping'

    id = Column(String(40))
    event_type = Column(String(40), ForeignKey('event_properties.event_type'))  # sign-in
    property_field_path = Column(String(255), ForeignKey('event_properties.field_path'))  # properties.email
    entity_name = Column(String(64))  # e.g. profile
    field_path = Column(String(255))  # data.pii.email.main
    field_type = Column(String(40))  # string
    converter = Column(String(40))  # lower

    # Additional fields for multi-tenancy
    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('ix_event_type_fields', 'event_type', 'property_field_path'),
    )

    running: bool = False


class EventToProfileMappingTable(Base):
    __tablename__ = 'event_to_profile_mapping'

    id = Column(String(40), index=True)
    name = Column(String(128))
    description = Column(Text)
    event_type_id = Column(String(40))
    event_type_name = Column(String(128))
    tags = Column(String(255))
    enabled = Column(Boolean, default=False)
    config = Column(JSON)
    event_to_profile = Column(JSON)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_collector', 'event_type_id', 'tenant', 'production', 'enabled')
    )

    running: bool = False


class EventDataComplianceTable(Base):
    __tablename__ = 'event_data_compliance'

    id = Column(String(40))
    name = Column(String(128))
    description = Column(Text)
    event_type_id = Column(String(40))
    event_type_name = Column(String(64))
    settings = Column(JSON)
    enabled = Column(Boolean, default=False)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_collector', 'event_type_id', 'tenant', 'production', 'enabled')
    )

    running: bool = False


class ActivationTable(Base):
    __tablename__ = 'activation'

    id = Column(String(40))
    name = Column(String(128))
    description = Column(Text)
    tags = Column(String(255))
    activation_type_id = Column(String(40))
    activation_type_name = Column(String(128))
    audience_id = Column(String(40))
    audience_name = Column(String(128))
    enabled = Column(Boolean, default=False)
    config = Column(JSON)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False


class ReportTable(Base):
    __tablename__ = 'report'

    id = Column(String(40))
    name = Column(String(128))
    description = Column(Text)
    tags = Column(String(128))
    index = Column(String(128))
    query = Column(JSON)
    enabled = Column(Boolean, default=True)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False

# TODO probably not used
class ImportTable(Base):
    __tablename__ = 'import'

    id = Column(String(40))
    name = Column(String(128))
    description = Column(Text)
    module = Column(String(255))
    config = Column(JSON)
    enabled = Column(Boolean, default=False)
    transitional = Column(Boolean)
    api_url = Column(String(255))
    event_source_id = Column(String(40))
    event_source_name = Column(String(128))
    event_type = Column(String(128))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False


class TaskTable(Base):
    __tablename__ = 'task'

    id = Column(String(40))
    timestamp = Column(DateTime)
    status = Column(String(64))
    name = Column(String(128))
    type = Column(String(64))
    progress = Column(Float)
    task_id = Column(String(40))
    params = Column(JSON)
    message = Column(Text)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
        Index('idx_gui', 'type', 'tenant', 'production')
    )

    running: bool = False


class SettingTable(Base):
    __tablename__ = 'setting'

    id = Column(String(40))
    timestamp = Column(DateTime)
    name = Column(String(128))
    description = Column(Text)
    type = Column(String(64))
    enabled = Column(Boolean, default=False)
    content = Column(JSON)
    config = Column(JSON)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False


class SubscriptionTable(Base):
    __tablename__ = 'subscription'

    id = Column(String(40))
    timestamp = Column(DateTime)
    name = Column(String(128))
    description = Column(Text)
    enabled = Column(Boolean, default=False)
    tags = Column(String(128))
    topic = Column(String(128))
    token = Column(String(64))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False


class TestTable(Base):
    __tablename__ = 'test'

    id = Column(String(40))
    timestamp = Column(DateTime)
    name = Column(String(128))
    event_source_id = Column(String(40))
    event_source_name = Column(String(128))
    event_type_id = Column(String(40))
    event_type_name = Column(String(64))
    profile_id = Column(String(40))
    session_id = Column(String(40))
    asynchronous = Column(Boolean)
    properties = Column(JSON)
    context = Column(JSON)

    tenant = Column(String(40))

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant'),
    )


class ConfigurationTable(Base):
    __tablename__ = 'configuration'

    id = Column(String(40))
    timestamp = Column(DateTime)
    name = Column(String(128))
    description = Column(Text)
    enabled = Column(Boolean, default=False)
    tags = Column(String(128))
    config = Column(JSON)
    ttl = Column(Integer, default=0)
    # cluster_wide_value = Column(Boolean)

    tenant = Column(String(40))

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant'),
    )


class AudienceTable(Base):
    __tablename__ = 'audience'

    id = Column(String(40))
    name = Column(String(128))
    description = Column(Text)
    enabled = Column(Boolean, default=False)
    tags = Column(Text)
    filter = Column(Text)
    join = Column(JSON)

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False
