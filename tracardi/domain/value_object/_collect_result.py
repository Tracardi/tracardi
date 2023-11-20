from dataclasses import dataclass
from typing import List

from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.utils.getters import get_entity_id


@dataclass
class CollectResult:
    session: List[BulkInsertResult]
    events: List[BulkInsertResult]
    profile: List[BulkInsertResult]

    def get_debugging_info(self, responses: List[dict], debugging: List[TrackerPayload]):
        for i, tracker_payload in enumerate(debugging):
            if tracker_payload.is_debugging_on():
                response = responses[i]
                if len(self.events) > 0:
                    event = self.events[0]
                    event_ids = event.ids
                else:
                    event_ids = []
                response['event'] = {
                    "ids": event_ids,
                    "saved": len(self.events)
                }
                response['session'] = {
                    "id": get_entity_id(tracker_payload.session),
                    "saved": len(self.session)
                }
                response['profile'].update({
                    "saved": len(self.profile)
                })
        return responses

