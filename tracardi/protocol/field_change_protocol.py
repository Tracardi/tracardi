from typing import Protocol

from tracardi.service.change_monitoring.field_change_monitor import FieldTimestampMonitor


class FieldChangeProtocol(Protocol):
    def set_metadata_fields_timestamps(self, field_timestamp_manager: FieldTimestampMonitor) -> None:
        ...