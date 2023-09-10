import logging
from typing import Optional, TypeVar, Type, Set
from uuid import uuid4
from pydantic import BaseModel, PrivateAttr

from tracardi.config import tracardi
from tracardi.domain.storage_record import RecordMetadata, StorageRecord
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.exceptions.log_handler import log_handler
from tracardi.protocol.operational import Operational
from tracardi.service.dot_notation_converter import dotter

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

T = TypeVar("T")


class Creatable(BaseModel):

    @classmethod
    def create(cls: Type[T], record: Optional[StorageRecord]) -> Optional[T]:
        if not record:
            return None

        obj = cls(**dict(record))

        if hasattr(obj, 'set_meta_data'):
            obj.set_meta_data(record.get_meta_data())
        return obj


class NullableEntity(Creatable):
    id: Optional[str] = None


class Entity(Creatable):
    id: str
    _metadata: Optional[RecordMetadata] = PrivateAttr(None)

    def set_meta_data(self, metadata: RecordMetadata = None) -> 'Entity':
        self._metadata = metadata
        return self

    def get_meta_data(self) -> Optional[RecordMetadata]:
        return self._metadata if isinstance(self._metadata, RecordMetadata) else None

    def has_meta_data(self) -> bool:
        return self._metadata is not None

    def to_storage_record(self, exclude=None, exclude_unset: bool = False) -> StorageRecord:
        record = StorageRecord(**self.model_dump(exclude=exclude, exclude_unset=exclude_unset))

        # Storage records must have ES _id

        if 'id' in record:
            record['_id'] = record['id']

        if self._metadata:
            record.set_meta_data(self._metadata)
        else:
            # Does not have metadata
            storage_info = self.storage_info()  # type: Optional[StorageInfo]
            if storage_info and storage_info.multi is True:
                if isinstance(self, Operational):
                    if self.operation.new is True:
                        logger.error(f"Entity {type(self)} does not have index set. And it is not new.")
                else:
                    logger.info(f"Entity {type(self)} converts to index-less storage record.")
        return record

    @staticmethod
    def new() -> 'Entity':
        return Entity(id=str(uuid4()))

    @staticmethod
    def storage_info() -> Optional[StorageInfo]:
        return None

    def get_dotted_properties(self) -> Set[str]:
        return dotter(self.model_dump())
