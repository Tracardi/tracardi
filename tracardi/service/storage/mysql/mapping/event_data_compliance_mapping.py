from tracardi.context import get_context
from tracardi.domain.consent_field_compliance import EventDataCompliance, ConsentFieldComplianceSetting
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.schema.table import EventDataComplianceTable
from tracardi.service.storage.mysql.utils.serilizer import to_model, from_model


def map_to_event_data_compliance_table(event_data_compliance: EventDataCompliance) -> EventDataComplianceTable:
    context = get_context()
    return EventDataComplianceTable(
        id=event_data_compliance.id,
        tenant=context.tenant,
        production=context.production,
        name=event_data_compliance.name,
        description=event_data_compliance.description or "",
        event_type_id=event_data_compliance.event_type.id,
        event_type_name=event_data_compliance.event_type.name,
        settings=from_model(event_data_compliance.settings),
        enabled=event_data_compliance.enabled if event_data_compliance.enabled is not None else False
    )


def map_to_event_data_compliance(event_data_compliance_table: EventDataComplianceTable) -> EventDataCompliance:
    return EventDataCompliance(
        id=event_data_compliance_table.id,
        name=event_data_compliance_table.name,
        description=event_data_compliance_table.description or "",
        event_type=NamedEntity(id=event_data_compliance_table.event_type_id, name=event_data_compliance_table.event_type_name),
        settings=to_model(event_data_compliance_table.settings, ConsentFieldComplianceSetting),
        enabled=event_data_compliance_table.enabled if event_data_compliance_table.enabled is not None else False,

        production=event_data_compliance_table.production,
        running=event_data_compliance_table.running
    )


