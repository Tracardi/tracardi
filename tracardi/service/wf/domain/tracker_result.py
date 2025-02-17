from dataclasses import dataclass
from typing import List, Optional, Dict

from tracardi.domain.flat_session import FlatSession
from tracardi.process_engine.debugger import Debugger
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.payload.tracker_payload import TrackerPayload


@dataclass
class TrackerResult:
    wf_triggered: bool
    tracker_payload: TrackerPayload
    events: List[Event]
    changed_field_timestamps: Dict[str, List]
    flat_session: Optional[FlatSession] = None
    profile: Optional[Profile] = None
    response: Optional[dict] = None
    debugger: Optional[Debugger] = None
    ux: Optional[list] = None

    def get_response_body(self, tracker_payload_id: str):
        body = {
            'task': tracker_payload_id,
            'ux': self.ux if self.ux else [],
            'response': self.response if self.response else {}

        }
        if self.profile:
            body["profile"] = {
                "id": self.profile.id
            }

        return body

    # def __repr__(self):
    #     return f"TrackerResult(ux={self.ux})"
