from tracardi.context import ServerContext, Context
from tracardi.domain.consent_type import ConsentType
from tracardi.service.storage.mysql.mapping.consent_type_mapping import map_to_consent_type_table, map_to_consent_type
from tracardi.service.storage.mysql.schema.table import ConsentTypeTable


def test_map_to_consent_type_table_correct_attributes():
    context = Context(tenant="test_tenant", production=True)

    with ServerContext(context):
        consent_type = ConsentType(
            id="1",
            name="Test Consent",
            description="This is a test consent",
            revokable=True,
            default_value="grant",
            enabled=True,
            tags=["tag1", "tag2"],
            auto_revoke="+1d"
        )

        consent_type_table = map_to_consent_type_table(consent_type)

        assert consent_type_table.production == context.production
        assert consent_type_table.name == consent_type.name
        assert consent_type_table.description == consent_type.description
        assert consent_type_table.revokable == consent_type.revokable
        assert consent_type_table.default_value == consent_type.default_value
        assert consent_type_table.enabled == consent_type.enabled
        assert consent_type_table.tags == ",".join(consent_type.tags)
        assert consent_type_table.required == False
        assert consent_type_table.auto_revoke == consent_type.auto_revoke


def test_map_all_fields_correctly():
    consent_type_table = ConsentTypeTable(
        id="123",
        name="Test Consent",
        description="This is a test consent",
        revokable=True,
        default_value="grant",
        enabled=True,
        tags="tag1,tag2",
        required=False,
        auto_revoke="+1d"
    )

    consent_type = map_to_consent_type(consent_type_table)

    assert consent_type.id == "123"
    assert consent_type.name == "Test Consent"
    assert consent_type.description == "This is a test consent"
    assert consent_type.revokable == True
    assert consent_type.default_value == "grant"
    assert consent_type.enabled == True
    assert consent_type.tags == ["tag1", "tag2"]
    assert consent_type.required == False
    assert consent_type.auto_revoke == "+1d"
