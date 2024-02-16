from tracardi.service.storage.mysql.service.bridge_service import BridgeService
from tracardi.service.storage.mysql.service.event_source_service import EventSourceService


def test_table_service():
    ess1 = EventSourceService()
    ess2 = EventSourceService()

    assert ess1 == ess2

    bs = BridgeService()

    assert bs != ess1