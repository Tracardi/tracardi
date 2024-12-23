import pytest
from uuid import uuid4
from tracardi.domain.consent_field_compliance import EventDataCompliance, ConsentFieldComplianceSetting, NamedEntity
from tracardi.context import ServerContext, Context
from tracardi.domain.ref_value import RefValue
from tracardi.service.storage.mysql.service.event_data_compliance_service import ConsentDataComplianceService


@pytest.mark.asyncio
async def test_consent_data_compliance_service():
    with ServerContext(Context(production=True)):
        # Initialize service
        service = ConsentDataComplianceService()

        # Test data setup
        data_compliance_id = uuid4().hex
        event_type = NamedEntity(id="event_type_id", name="event_type_name")
        settings = [ConsentFieldComplianceSetting(
            action="Remove",
            field=RefValue(ref=False, value="value"),
            consents=[NamedEntity(id="consent_id", name="consent_name")]
        )]
        data_compliance = EventDataCompliance(
            id=data_compliance_id,
            name="Test Compliance",
            description="Test Description",
            event_type=event_type,
            settings=settings,
            enabled=True
        )

        # Insert Data Compliance
        await service.insert(data_compliance)

        # Load All Data Compliance
        all_data_compliances = await service.load_all()
        assert any(compliance.id == data_compliance_id for compliance in all_data_compliances.rows)

        # Load Data Compliance by ID
        loaded_data_compliance = await service.load_by_id(data_compliance_id)
        assert loaded_data_compliance.rows.id == data_compliance_id

        # Load Data Compliance by Event Type
        compliance_by_event_type = await service.load_by_event_type(event_type_id="event_type_id")
        assert any(compliance.event_type_id == "event_type_id" for compliance in compliance_by_event_type.rows)

        # Delete Data Compliance by ID
        await service.delete_by_id(data_compliance_id)

        # Verify Deletion
        deleted_data_compliance = await service.load_by_id(data_compliance_id)
        assert deleted_data_compliance.rows is None
