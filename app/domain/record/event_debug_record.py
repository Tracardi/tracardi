import base64
import json
from typing import Dict, List

from pydantic import BaseModel
from tracardi_graph_runner.domain.debug_info import DebugInfo

from app.domain.entity import Entity
from app.domain.value_object.tracker_payload_result import TrackerPayloadResult
from app.service.storage.crud import StorageCrud


class EventDebugRecord(BaseModel):
    event: Entity
    content: str

    @staticmethod
    def encode(stat: Dict[str, List[Dict[str, DebugInfo]]]) -> List['EventDebugRecord']:

        for event_type, debugging in stat.items():
            for debug_infos in debugging:
                for rule_id, debug_info in debug_infos.items():

                    json_init = json.dumps(debug_info.dict(), default=str)
                    b64 = base64.b64encode(json_init.encode('utf-8'))

                    yield EventDebugRecord(event=Entity(id=debug_info.event.id), content=b64)

    def decode(self) -> DebugInfo:
        decoded = base64.b64decode(self.content)
        debug_info = json.loads(decoded)
        return DebugInfo(
            **debug_info
        )

    # Persistence

    def storage(self) -> StorageCrud:
        return StorageCrud("debug-info", TrackerPayloadResult, entity=self)
