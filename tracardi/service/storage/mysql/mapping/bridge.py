from tracardi.context import get_context
from tracardi.domain.bridge import Bridge
from tracardi.service.plugin.domain.register import Form
from tracardi.service.storage.mysql.table import BridgeTable
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json


def map_to_table(bridge: Bridge) -> BridgeTable:
    context = get_context()
    return BridgeTable(
        id=bridge.id,
        tenant=context.tenant,
        production=context.production,
        name=bridge.name,
        description=bridge.description,
        type=bridge.type,
        config=to_json(bridge.config),
        form=to_json(bridge.form),
        manual=bridge.manual
    )


def map_to_bridge(bridge_table: BridgeTable) -> Bridge:

    return Bridge(
        id=bridge_table.id,
        name=bridge_table.name,
        description=bridge_table.description,
        type=bridge_table.type,
        config=from_json(bridge_table.config),
        form=from_json(bridge_table.form, Form),
        manual=bridge_table.manual
    )
