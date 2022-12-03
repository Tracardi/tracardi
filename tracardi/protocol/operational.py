from typing import Protocol, runtime_checkable

from tracardi.domain.value_object.operation import RecordFlag


@runtime_checkable
class Operational(Protocol):
    operation: RecordFlag
