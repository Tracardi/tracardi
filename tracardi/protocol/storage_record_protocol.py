from typing import Protocol, Optional

from tracardi.domain.storage_record import RecordMetadata, StorageRecord


class StorageRecordProtocol(Protocol):
    def set_meta_data(self, meta: RecordMetadata) -> 'StorageRecord':
       pass

    def get_meta_data(self) -> Optional[RecordMetadata]:
        pass

    def has_meta_data(self) -> bool:
        pass