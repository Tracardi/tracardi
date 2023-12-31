from tracardi.context import get_context, Context, ServerContext
from tracardi.domain.bridge import Bridge
from tracardi.service.plugin.domain.register import Form
from tracardi.service.storage.mysql.mapping.bridge_mapping import map_to_bridge, map_to_bridge_table
from tracardi.service.storage.mysql.schema.table import BridgeTable
from tracardi.service.storage.mysql.utils.serilizer import from_model


def test_all_fields_mapped_correctly():
    bridge_table = BridgeTable(
        id="123",
        tenant="test",
        name="Test Bridge",
        description="This is a test bridge",
        type="event",
        config={"key": "value"},
        form={"submit": "Submit", "default": {}, "title": "Form Title", "groups": []},
        manual="This is a manual"
    )

    expected_bridge = Bridge(
        id="123",
        name="Test Bridge",
        description="This is a test bridge",
        type="event",
        config={"key": "value"},
        form=Form(submit="Submit", default={}, title="Form Title", groups=[]),
        manual="This is a manual"
    )

    assert map_to_bridge(bridge_table) == expected_bridge

def test_returns_bridge_table_with_same_fields():
    with ServerContext(Context(production=True)):
        bridge = Bridge(
            id="123",
            name="Test Bridge",
            description="This is a test bridge",
            type="event-collect",
            config={"key": "value"},
            form=Form(),
            manual="Some manual"
        )

        expected_table = BridgeTable(
            id="123",
            tenant=get_context().tenant,
            name="Test Bridge",
            description="This is a test bridge",
            type="event-collect",
            config={"key": "value"},
            form=from_model(Form()),
            manual="Some manual"
        )

        table = map_to_bridge_table(bridge)

        assert table.id == expected_table.id
        assert table.tenant == expected_table.tenant
        assert table.name == expected_table.name
        assert table.description == expected_table.description
        assert table.config == expected_table.config
        assert table.form == expected_table.form
        assert table.manual == expected_table.manual