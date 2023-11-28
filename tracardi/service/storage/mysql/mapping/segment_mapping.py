from tracardi.context import get_context
from tracardi.domain.segment import Segment
from tracardi.service.storage.mysql.schema.table import SegmentTable


def map_to_segment_table(segment: Segment) -> SegmentTable:
    context = get_context()

    return SegmentTable(
        id=segment.id,
        name=segment.name,
        description=segment.description,
        event_type=','.join(segment.eventType) if segment.eventType else None,
        condition=segment.condition,
        enabled=segment.enabled,
        machine_name=segment.machine_name,

        tenant=context.tenant,
        production=context.production
    )

def map_to_segment(segment_table: SegmentTable) -> Segment:
    return Segment(
        id=segment_table.id,
        name=segment_table.name,
        description=segment_table.description,
        eventType=segment_table.event_type.split(',') if segment_table.event_type else [],
        condition=segment_table.condition,
        enabled=segment_table.enabled,
        machine_name=segment_table.machine_name
        # Assuming tenant and production are not required in Segment constructor
    )
