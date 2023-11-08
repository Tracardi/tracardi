import json

from tracardi.domain.bridge import Bridge
from tracardi.service.plugin.domain.register import Form
from tracardi.service.storage.mysql.table import BridgeTable
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json


def map_to_table(bridge: Bridge) -> BridgeTable:
    return BridgeTable(
        id=bridge.id,
        name=bridge.name,
        description=bridge.description,
        type=bridge.type,
        config=to_json(bridge.config),
        form=to_json(bridge.form),
        manual=bridge.manual
    )


def map_to_object(bridge_table: BridgeTable) -> Bridge:
    return Bridge(
        id=bridge_table.id,
        name=bridge_table.name,
        description=bridge_table.description,
        type=bridge_table.type,
        config=from_json(bridge_table.config),
        form=from_json(bridge_table.form, Form),
        manual=bridge_table.manual
    )
