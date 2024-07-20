from typing import Optional, TypeVar, Type, Set, List
from uuid import uuid4
from pydantic import BaseModel, PrivateAttr

from tracardi.domain import ExtraInfo
from tracardi.domain.storage_record import RecordMetadata, StorageRecord
from tracardi.domain.time import Time
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.exceptions.log_handler import get_logger
from tracardi.protocol.operational import Operational
from tracardi.service.dot_notation_converter import dotter
from tracardi.service.storage.index import Resource

logger = get_logger(__name__)

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


class NullablePrimaryEntity(NullableEntity):
    primary_id: Optional[str] = None


class Entity(Creatable):
    id: str
    _metadata: Optional[RecordMetadata] = PrivateAttr(None)

    def set_meta_data(self, metadata: RecordMetadata = None) -> 'Entity':
        self._metadata = metadata
        return self

    def get_meta_data(self) -> Optional[RecordMetadata]:
        return self._metadata if isinstance(self._metadata, RecordMetadata) else None

    def _fill_meta_data(self, index_type: str):
        """
        Used to fill metadata with default current index and id.
        """
        if not self.has_meta_data():
            resource = Resource()
            self.set_meta_data(RecordMetadata(id=self.id, index=resource[index_type].get_write_index()))

    def dump_meta_data(self) -> Optional[dict]:
        return self._metadata.model_dump(mode='json') if isinstance(self._metadata, RecordMetadata) else None

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
                    if self.operation.new is False:
                        # This is critical error of the system. It should be reported to the vendor.
                        logger.error(
                            f"Entity {type(self)} does not have index set. And it is not new.",
                            extra=ExtraInfo.build(object=self, origin="storage", error_number="S0001")
                        )
                else:
                    # This is critical warning of the system. It should be reported to the vendor.
                    logger.warning(
                        f"Entity {type(self)} converts to index-less storage record.",
                        extra=ExtraInfo.build(object=self, origin="storage", error_number="S0002")
                    )
        return record

    @staticmethod
    def new() -> 'Entity':
        return Entity(id=str(uuid4()))

    @staticmethod
    def storage_info() -> Optional[StorageInfo]:
        return None

    def get_dotted_properties(self) -> Set[str]:
        return dotter(self.model_dump())

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id if isinstance(other, Entity) else False


class DefaultEntity(Entity):
    metadata: Optional[Time] = None


class PrimaryEntity(Entity):
    primary_id: Optional[str] = None
    metadata: Optional[Time] = None
    ids: Optional[List[str]] = None
