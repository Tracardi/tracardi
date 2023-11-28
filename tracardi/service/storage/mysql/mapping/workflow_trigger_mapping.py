import json

from tracardi.context import get_context
from tracardi.domain.metadata import Metadata
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.rule import Rule
from tracardi.domain.time import Time
from tracardi.service.storage.mysql.schema.table import TriggerTable
from tracardi.service.storage.mysql.utils.serilizer import to_json


def map_to_workflow_trigger_table(rule: Rule) -> TriggerTable:
    context = get_context()

    return TriggerTable(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        type=rule.type,
        metadata_time_insert=rule.metadata.time.insert if rule.metadata and rule.metadata.time else None,
        event_type_id=rule.event_type.id if rule.event_type else None,
        event_type_name=rule.event_type.name if rule.event_type else None,
        flow_id=rule.flow.id if rule.flow else None,
        flow_name=rule.flow.name if rule.flow else None,
        segment_id=rule.segment.id if rule.segment else None,
        segment_name=rule.segment.name if rule.segment else None,
        source_id=rule.source.id if rule.source else None,
        source_name=rule.source.name if rule.source else None,
        properties=to_json(rule.properties) if rule.properties else None,
        enabled=rule.enabled,
        tags=",".join(rule.tags) if rule.tags else None,

        tenant=context.tenant,
        production=context.production
    )

def map_to_workflow_trigger_rule(trigger_table: TriggerTable) -> Rule:
    return Rule(
        id=trigger_table.id,
        name=trigger_table.name,
        description=trigger_table.description,
        type=trigger_table.type,
        metadata=Metadata(time=Time(insert=trigger_table.metadata_time_insert)) if trigger_table.metadata_time_insert else None,
        event_type=NamedEntity(id=trigger_table.event_type_id, name=trigger_table.event_type_name) if trigger_table.event_type_id else None,
        flow=NamedEntity(id=trigger_table.flow_id, name=trigger_table.flow_name) if trigger_table.flow_id else None,
        segment=NamedEntity(id=trigger_table.segment_id, name=trigger_table.segment_name) if trigger_table.segment_id else None,
        source=NamedEntity(id=trigger_table.source_id, name=trigger_table.source_name) if trigger_table.source_id else None,
        properties=json.loads(trigger_table.properties) if trigger_table.properties else None,
        enabled=trigger_table.enabled if trigger_table.enabled is not None else False,
        tags=trigger_table.tags.split(",") if trigger_table.tags else None
    )
