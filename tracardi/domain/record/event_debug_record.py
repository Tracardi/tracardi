from typing import Dict, List

from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.process_engine.debugger import Debugger
from tracardi.service.wf.domain.debug_info import DebugInfo
from tracardi.domain.entity import Entity
from tracardi.service.secrets import b64_encoder, b64_decoder


class EventDebugRecord(Entity):
    content: str = None

    @staticmethod
    def encode(stat: Debugger) -> List['EventDebugRecord']:

        for event_type, debugging in stat.items():
            for debug_infos in debugging:
                for rule_id, debug_info in debug_infos.items():  # type: DebugInfo
                    # todo - to pole jest za małe (wyskakuje błąd gdy debug infor ma powyżej 32000 znaków)
                    b64 = b64_encoder(debug_info.dict())
                    yield EventDebugRecord(id=debug_info.event.id, content=b64)

    def decode(self, from_dict=False) -> DebugInfo:
        # todo - to pole jest za małe (wyskakuje błąd gdy debug infor ma powyżej 32000 znaków)
        if from_dict is True:
            debug_info = b64_decoder(self['content'])
        else:
            debug_info = b64_decoder(self.content)

        return DebugInfo(
            **debug_info
        )

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'debug-info',
            EventDebugRecord
        )
