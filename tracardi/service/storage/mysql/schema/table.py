from sqlalchemy import and_

from sqlalchemy import (Column, String, DateTime, Boolean, JSON, LargeBinary,
                        ForeignKey, PrimaryKeyConstraint, Text, Integer)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from tracardi.context import get_context

Base = declarative_base()


def local_context_filter(table: Base):
    context = get_context()
    return and_(table.tenant == context.tenant, table.production == context.production)


def local_context_entity(table: Base, id):
    context = get_context()
    return and_(table.tenant == context.tenant, table.production == context.production, table.id == id)

class BridgeTable(Base):
    __tablename__ = 'bridge'

    id = Column(String(40))  # 'keyword' with ignore_above maps to VARCHAR with length
    tenant = Column(String(40))
    production = Column(Boolean)
    name = Column(String(64))  # 'text' type in ES maps to VARCHAR(255) in MySQL
    description = Column(Text)  # 'text' type in ES maps to VARCHAR(255) in MySQL
    type = Column(String(48))  # 'keyword' type in ES maps to VARCHAR(255) in MySQL
    config = Column(JSON)  # 'object' type in ES with 'enabled' false maps to JSON in MySQL
    form = Column(JSON)  # 'object' type in ES with 'enabled' false maps to JSON in MySQL
    manual = Column(Text, nullable=True)  # 'keyword' type in ES with 'index' false maps to VARCHAR(255) in MySQL

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )


class EventSourceTable(Base):
    __tablename__ = 'event_source'

    id = Column(String(40), primary_key=True)
    tenant = Column(String(40))
    production = Column(Boolean)
    timestamp = Column(DateTime)
    update = Column(DateTime)
    type = Column(String(32))
    bridge_id = Column(String(40))
    bridge_name = Column(String(128), ForeignKey('bridge.id'))
    name = Column(String(64))
    description = Column(String(255))
    channel = Column(String(32))
    url = Column(String(255))
    enabled = Column(Boolean)
    locked = Column(Boolean)
    transitional = Column(Boolean)
    tags = Column(String(255))
    groups = Column(String(255))
    icon = Column(String(32))
    config = Column(JSON)
    configurable = Column(Boolean)
    hash = Column(String(255))
    returns_profile = Column(Boolean)
    permanent_profile_id = Column(Boolean)
    requires_consent = Column(Boolean)
    synchronize_profiles = Column(Boolean)
    manual = Column(String(64))
    endpoints_get_url = Column(String(255))
    endpoints_get_method = Column(String(255))
    endpoints_post_url = Column(String(255))
    endpoints_post_method = Column(String(255))

    bridge = relationship("BridgeTable")


class WorkflowTable(Base):
    __tablename__ = 'workflow'

    id = Column(String(40), primary_key=True)
    tenant = Column(String(40))
    production = Column(Boolean)
    timestamp = Column(DateTime)
    deploy_timestamp = Column(DateTime)
    name = Column(String(64))
    description = Column(String(255))
    type = Column(String(64), default="collection")
    projects = Column(String(255))
    draft = Column(LargeBinary)
    production = Column(LargeBinary)
    backup = Column(LargeBinary)
    lock = Column(Boolean)
    deployed = Column(Boolean, default=False)
    debug_enabled = Column(Boolean)
    debug_logging_level = Column(String(32))


class TriggerTable(Base):
    __tablename__ = 'trigger'

    id = Column(String(40), primary_key=True)  # 'keyword' in ES with ignore_above
    tenant = Column(String(40))
    production = Column(Boolean)
    name = Column(String(150))  # 'keyword' in ES with ignore_above
    description = Column(String(255))  # 'text' in ES with no string length mentioned
    type = Column(String(64))  # 'keyword' in ES defaults to 255 if no ignore_above is set
    metadata_time_insert = Column(DateTime)  # Nested 'date' fields
    event_type_id = Column(String(40))  # Nested 'keyword' fields
    event_type_name = Column(String(64))  # Nested 'keyword' fields
    flow_id = Column(String(40))  # Nested 'keyword' fields
    flow_name = Column(String(64))  # Nested 'text' fields with no string length mentioned
    segment_id = Column(String(40))  # Nested 'keyword' fields
    segment_name = Column(String(64))  # Nested 'text' fields with no string length mentioned
    source_id = Column(String(40))  # Nested 'keyword' fields
    source_name = Column(String(64))  # Nested 'text' fields with no string length mentioned
    properties = Column(JSON)  # 'object' in ES is mapped to 'JSON' in MySQL
    enabled = Column(Boolean)  # 'boolean' in ES is mapped to BOOLEAN in MySQL
    tags = Column(String(255))  # 'keyword' in ES defaults to 255 if no ignore_above is set


class ResourceTable(Base):
    __tablename__ = 'resource'

    id = Column(String(40), primary_key=True)
    tenant = Column(String(40))
    production = Column(Boolean)
    type = Column(String(48))
    timestamp = Column(DateTime)
    name = Column(String(64))
    description = Column(String(255))
    credentials = Column(String(255))
    enabled = Column(Boolean)
    tags = Column(String(255))
    groups = Column(String(255))
    icon = Column(String(255))
    destination = Column(String(255))


class PluginTable(Base):
    __tablename__ = 'plugin'

    id = Column(String(64))
    tenant = Column(String(40))
    production = Column(Boolean)
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
    plugin_metadata_keywords = Column(String(256))
    plugin_metadata_name = Column(String(64))
    plugin_metadata_type = Column(String(24))
    plugin_metadata_tags = Column(String(32))
    plugin_metadata_pro = Column(Boolean)
    plugin_metadata_commercial = Column(Boolean)
    plugin_metadata_remote = Column(Boolean)
    plugin_metadata_documentation = Column(Text)
    plugin_metadata_frontend = Column(Boolean)
    plugin_metadata_emits_event = Column(Text)
    plugin_metadata_purpose = Column(String(255))
    plugin_spec_id = Column(String(64))
    plugin_spec_class_name = Column(String(32))
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
    plugin_spec_manual = Column(Text)
    plugin_spec_author = Column(String(64))
    plugin_spec_license = Column(String(32))
    plugin_spec_version = Column(String(32))
    plugin_start = Column(Boolean)
    plugin_spec_run_once_value = Column(String(64))
    plugin_spec_run_once_ttl = Column(Integer)
    plugin_spec_run_once_type = Column(String(255))
    plugin_spec_run_once_enabled = Column(Boolean)
    plugin_spec_node_on_remove = Column(String(128))
    plugin_spec_node_on_create = Column(String(128))
    settings_enabled = Column(Boolean)
    settings_hidden = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )
