from tracardi.context import get_context
from tracardi.domain.consent_field_compliance import ConsentFieldCompliance, ConsentFieldComplianceSetting
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.schema.table import EventDataComplianceTable
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json


def map_to_event_data_compliance_table(event_data_compliance: ConsentFieldCompliance) -> EventDataComplianceTable:
    context = get_context()
    return EventDataComplianceTable(
        id=event_data_compliance.id,
        tenant=context.tenant,
        production=context.production,
        name=event_data_compliance.name,
        description=event_data_compliance.description or "",
        event_type_id=event_data_compliance.event_type.id,
        event_type_name=event_data_compliance.event_type.name,
        settings=to_json(event_data_compliance.settings),
        enabled=event_data_compliance.enabled if event_data_compliance.enabled is None else False
    )


def map_to_event_data_compliance(event_data_compliance_table: EventDataComplianceTable) -> ConsentFieldCompliance:
    return ConsentFieldCompliance(
        id=event_data_compliance_table.id,
        name=event_data_compliance_table.name,
        description=event_data_compliance_table.description or "",
        event_type=NamedEntity(id=event_data_compliance_table.event_type_id, name=event_data_compliance_table.event_type_name),
        settings=from_json(event_data_compliance_table.settings, ConsentFieldComplianceSetting),
        enabled=event_data_compliance_table.enabled if event_data_compliance_table.enabled is None else False
    )


