import pytest
from datetime import datetime

from tracardi.context import get_context, ServerContext, Context
from tracardi.domain.event_source import EventSource
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.mapping.event_source_mapping import map_to_event_source_table, map_to_event_source
from tracardi.service.storage.mysql.schema.table import EventSourceTable


def test_create_instance_with_required_parameters():
    event_source = EventSource(
        id="1",
        type=["rest"],
        name="test",
        bridge=NamedEntity(id="1", name="API")
    )
    assert event_source.type == ["rest"]
    assert event_source.bridge == NamedEntity(id="1", name="API")
    assert event_source.timestamp is not None
    assert isinstance(event_source.timestamp, datetime)


def test_create_instance_with_invalid_timestamp_should_raise_exception():
    with pytest.raises(Exception):
        EventSource(
            id="2",
            type=["rest"],
            bridge=NamedEntity(id="1", name="API"),
            timestamp="invalid"
        )


def test_mapping_event_source_to_table():

    with ServerContext(Context(production=True)):

        event_source = EventSource(
            id="1",
            type=["type1", "type2"],
            bridge=NamedEntity(id="bridge_id", name="bridge_name"),
            name="Event Source",
            description="Event Source Description",
            channel="channel",
            tags=["tag1", "tag2"],
            groups=["group1", "group2"],
            config={"key": "value"}
        )

        event_source_table = map_to_event_source_table(event_source)

        assert isinstance(event_source_table, EventSourceTable)
        assert event_source_table.id == event_source.id
        assert event_source_table.type == "type1,type2"
        assert event_source_table.bridge_id == event_source.bridge.id
        assert event_source_table.bridge_name == event_source.bridge.name
        assert event_source_table.timestamp == event_source.timestamp
        assert event_source_table.name == event_source.name
        assert event_source_table.description == event_source.description
        assert event_source_table.channel == event_source.channel
        assert event_source_table.enabled == event_source.enabled
        assert event_source_table.transitional == event_source.transitional
        assert event_source_table.tags == "tag1,tag2"
        assert event_source_table.groups == "group1,group2"
        assert event_source_table.permanent_profile_id == event_source.permanent_profile_id
        assert event_source_table.requires_consent == event_source.requires_consent
        assert event_source_table.manual == event_source.manual
        assert event_source_table.locked == event_source.locked
        assert event_source_table.synchronize_profiles == event_source.synchronize_profiles
        assert event_source_table.config == event_source.config
        assert event_source_table.tenant == get_context().tenant
        assert event_source_table.production == get_context().production
        assert event_source_table.update.date() == datetime.now().date()

        assert event_source_table.production is True

        assert event_source_table.url is None
        assert event_source_table.icon is None
        assert event_source_table.hash is None
        assert event_source_table.endpoints_get_url is None
        assert event_source_table.endpoints_get_method is None
        assert event_source_table.endpoints_post_url is None
        assert event_source_table.endpoints_post_method is None
        assert event_source_table.configurable is None

def test_returns_instance_with_all_attributes():
    event_source_table = EventSourceTable(
        id="test_id",
        type="test_type",
        bridge_id="test_bridge_id",
        bridge_name="test_bridge_name",
        name="test_name",
        description="test_description",
        channel="test_channel",
        tags="test_tag1,test_tag2",
        groups="test_group1,test_group2",
        manual="test_manual",
        config={"key": "value"},
        enabled=True,
        synchronize_profiles=True,
        locked=False,
        transitional=False,
        permanent_profile_id=False,
        requires_consent=False
    )

    print(event_source_table.enabled)

    event_source = map_to_event_source(event_source_table)
    assert isinstance(event_source, EventSource)
    assert event_source.id == "test_id"
    assert event_source.type == ["test_type"]
    assert isinstance(event_source.bridge, NamedEntity)
    assert event_source.bridge.id == "test_bridge_id"
    assert event_source.bridge.name == "test_bridge_name"
    assert isinstance(event_source.timestamp, datetime)
    assert event_source.name == "test_name"
    assert event_source.description == "test_description"
    assert event_source.channel == "test_channel"
    assert event_source.enabled is True
    assert event_source.transitional is False
    assert event_source.tags == ["test_tag1", "test_tag2"]
    assert event_source.groups == ["test_group1", "test_group2"]
    assert event_source.permanent_profile_id is False
    assert event_source.requires_consent is False
    assert event_source.manual == "test_manual"
    assert event_source.locked is False
    assert event_source.synchronize_profiles is True
    assert event_source.config == {"key": "value"}
