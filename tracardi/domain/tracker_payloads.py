from typing import Dict, List

from tracardi.domain.payload.tracker_payload import TrackerPayload


class TrackerPayloads(Dict[str, List[TrackerPayload]]):
    def serialize(self) -> dict:
        return {key: [v.dict() for v in values] for key, values in self.items()}

    @staticmethod
    def deserialize(data: dict) -> 'TrackerPayloads':
        tp = TrackerPayloads()
        for key, values in data.items():
            tp[key] = [TrackerPayload(**v) for v in values]
        return tp
