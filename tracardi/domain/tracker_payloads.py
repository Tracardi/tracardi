from typing import List

from tracardi.domain.payload.tracker_payload import TrackerPayload


class TrackerPayloads(List[TrackerPayload]):
    def serialize(self) -> List[dict]:
        return [v.dict() for v in self]

    @staticmethod
    def deserialize(data: dict) -> 'TrackerPayloads':
        return TrackerPayloads([TrackerPayload(**v) for v in data])

