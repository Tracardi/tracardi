from typing import Protocol, runtime_checkable

@runtime_checkable
class JsonSerializable(Protocol):
    def serialize(self):
        pass

    @staticmethod
    def deserialize(data):
        pass

