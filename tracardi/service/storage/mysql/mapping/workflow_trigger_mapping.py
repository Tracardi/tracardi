from tracardi.context import get_context
from tracardi.domain.metadata import Metadata
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.rule import Rule
from tracardi.domain.time import Time
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import WorkflowTriggerTable


def map_to_workflow_trigger_table(workflow_trigger: Rule) -> WorkflowTriggerTable:
    context = get_context()

    return WorkflowTriggerTable(
        id=workflow_trigger.id,
        name=workflow_trigger.name,
        description=workflow_trigger.description,
        type=workflow_trigger.type,
        metadata_time_insert=workflow_trigger.metadata.time.insert if workflow_trigger.metadata and workflow_trigger.metadata.time else None,
        event_type_id=workflow_trigger.event_type.id if workflow_trigger.event_type else None,
        event_type_name=workflow_trigger.event_type.name if workflow_trigger.event_type else None,
        flow_id=workflow_trigger.flow.id if workflow_trigger.flow else None,
        flow_name=workflow_trigger.flow.name if workflow_trigger.flow else None,
        segment_id=workflow_trigger.segment.id if workflow_trigger.segment else None,
        segment_name=workflow_trigger.segment.name if workflow_trigger.segment else None,
        source_id=workflow_trigger.source.id if workflow_trigger.source else None,
        source_name=workflow_trigger.source.name if workflow_trigger.source else None,
        properties=workflow_trigger.properties,
        enabled=workflow_trigger.enabled,
        tags=",".join(workflow_trigger.tags) if workflow_trigger.tags else None,

        tenant=context.tenant,
        production=context.production
    )


def map_to_workflow_trigger_rule(trigger_table: WorkflowTriggerTable) -> Rule:
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
        properties=trigger_table.properties,
        enabled=trigger_table.enabled if trigger_table.enabled is not None else False,
        tags=split_list(trigger_table.tags),
        production=trigger_table.production,
        running=trigger_table.running
    )
