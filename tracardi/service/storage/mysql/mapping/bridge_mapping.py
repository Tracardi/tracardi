from tracardi.context import get_context
from tracardi.domain.bridge import Bridge
from tracardi.service.plugin.domain.register import Form
from tracardi.service.storage.mysql.schema.table import BridgeTable
from tracardi.service.storage.mysql.utils.serilizer import to_model, from_model


def map_to_bridge_table(bridge: Bridge) -> BridgeTable:
    context = get_context()
    return BridgeTable(
        id=bridge.id,
        tenant=context.tenant,
        name=bridge.name,
        description=bridge.description,
        type=bridge.type,
        config=bridge.config,
        form=from_model(bridge.form),
        manual=bridge.manual
    )


def map_to_bridge(bridge_table: BridgeTable) -> Bridge:

    return Bridge(
        id=bridge_table.id,
        name=bridge_table.name,
        description=bridge_table.description,
        type=bridge_table.type,
        config=bridge_table.config,
        form=to_model(bridge_table.form, Form),
        manual=bridge_table.manual
    )
