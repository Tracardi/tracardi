from datetime import datetime

from tracardi.context import ServerContext, Context
from tracardi.domain.metadata import Metadata
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.rule import Rule
from tracardi.domain.time import Time
from tracardi.service.storage.mysql.mapping.workflow_trigger_mapping import map_to_workflow_trigger_table, \
    map_to_workflow_trigger_rule
from tracardi.service.storage.mysql.schema.table import WorkflowTriggerTable
from tracardi.service.storage.mysql.utils.serilizer import to_json


def test_valid_rule_mapping():
    with ServerContext(Context(production=True)):
        rule = Rule(
            id="123",
            name="Test Rule",
            description="This is a test rule",
            type="event-collect",
            metadata=Metadata(
                time=Time(
                    insert=datetime.utcnow()
                )
            ),
            event_type=NamedEntity(
                id="event_type_1",
                name="Event Type 1"
            ),
            flow=NamedEntity(
                id="flow_1",
                name="Flow 1"
            ),
            segment=NamedEntity(
                id="segment_1",
                name="Segment 1"
            ),
            source=NamedEntity(
                id="source_1",
                name="Source 1"
            ),
            properties={
                "property1": "value1",
                "property2": "value2"
            },
            tags=["Tag1", "Tag2"]
        )

        trigger_table = map_to_workflow_trigger_table(rule)

        assert trigger_table.id == "123"
        assert trigger_table.name == "Test Rule"
        assert trigger_table.description == "This is a test rule"
        assert trigger_table.type == "event-collect"
        assert trigger_table.metadata_time_insert == rule.metadata.time.insert
        assert trigger_table.event_type_id == "event_type_1"
        assert trigger_table.event_type_name == "Event Type 1"
        assert trigger_table.flow_id == "flow_1"
        assert trigger_table.flow_name == "Flow 1"
        assert trigger_table.segment_id == "segment_1"
        assert trigger_table.segment_name == "Segment 1"
        assert trigger_table.source_id == "source_1"
        assert trigger_table.source_name == "Source 1"
        assert trigger_table.properties == {"property1": "value1", "property2": "value2"}
        assert trigger_table.enabled is True
        assert trigger_table.tags == "Tag1,Tag2"
        assert trigger_table.production == True


def test_valid_trigger_table():
    trigger_table = WorkflowTriggerTable(
        id="123",
        tenant="test",
        production=True,
        name="Test Trigger",
        description="This is a test trigger",
        type="event",
        metadata_time_insert=datetime.utcnow(),
        event_type_id="456",
        event_type_name="Test Event",
        flow_id="789",
        flow_name="Test Flow",
        segment_id="abc",
        segment_name="Test Segment",
        source_id="def",
        source_name="Test Source",
        properties={"key": "value"},
        enabled=True,
        tags="tag1,tag2"
    )

    expected_rule = Rule(
        id="123",
        name="Test Trigger",
        description="This is a test trigger",
        type="event",
        metadata=Metadata(time=Time(insert=datetime.utcnow())),
        event_type=NamedEntity(id="456", name="Test Event"),
        flow=NamedEntity(id="789", name="Test Flow"),
        segment=NamedEntity(id="abc", name="Test Segment"),
        source=NamedEntity(id="def", name="Test Source"),
        properties={"key": "value"},
        enabled=True,
        tags=["tag1", "tag2"]
    )

    assert map_to_workflow_trigger_rule(trigger_table) == expected_rule
