from tracardi.context import ServerContext, Context
from tracardi.domain.consent_field_compliance import EventDataCompliance, ConsentFieldComplianceSetting
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.ref_value import RefValue
from tracardi.service.storage.mysql.mapping.event_data_compliance_mapping import map_to_event_data_compliance_table, \
    map_to_event_data_compliance
from tracardi.service.storage.mysql.schema.table import EventDataComplianceTable
from tracardi.service.storage.mysql.utils.serilizer import from_model


def test_table_mapping():

    settings = [
                ConsentFieldComplianceSetting(
                    action="hash",
                    field=RefValue(ref=True, value="profile@email"),
                    consents=[NamedEntity(name="Setting 2", id="Value 2")]
                )
            ]

    with ServerContext(Context(production=True)) as context:
        event_data_compliance = EventDataCompliance(
            id="123",
            name="Example Compliance",
            description="This is an example compliance",
            event_type=NamedEntity(id="456", name="Example Event Type"),
            settings=settings,
            enabled=True
        )

        result = map_to_event_data_compliance_table(event_data_compliance)

        assert isinstance(result, EventDataComplianceTable)
        assert result.id == "123"
        assert result.production == context.context.production
        assert result.name == "Example Compliance"
        assert result.description == "This is an example compliance"
        assert result.event_type_id == "456"
        assert result.event_type_name == "Example Event Type"
        assert result.settings == from_model(settings)
        assert result.enabled is True

def test_correctly_map_all_fields():
    settings = [
        ConsentFieldComplianceSetting(
            action="hash",
            field=RefValue(ref=True, value="profile@email"),
            consents=[NamedEntity(name="Setting 2", id="Value 2")]
        )
    ]

    event_data_compliance_table = EventDataComplianceTable(
        id="1",
        name="Test",
        event_type_id="2",
        event_type_name="Test event type",
        settings=from_model(settings),
        enabled=True
    )

    expected_result = EventDataCompliance(
        id="1",
        name="Test",
        description="",
        event_type=NamedEntity(id="2", name="Test event type"),
        settings=settings,
        enabled=True
    )
    result = map_to_event_data_compliance(event_data_compliance_table)

    assert result.id == expected_result.id
    assert result.name == expected_result.name
    assert result.description == expected_result.description
    assert result.event_type == expected_result.event_type
    assert result.settings == expected_result.settings
    assert result.enabled == expected_result.enabled
