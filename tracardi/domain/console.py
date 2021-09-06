from datetime import datetime
from typing import Any
from pydantic import BaseModel


class Metadata(BaseModel):
    timestamp: datetime = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.timestamp = datetime.utcnow()


class Console(BaseModel):
    metadata: Metadata = Metadata()
    event_id: str
    flow_id: str
    origin: str
    class_name: str
    module: str
    type: str
    message: str

    # # Persistence
    #
    # def storage(self) -> StorageCrud:
    #     return StorageCrud("console-log", Console, entity=self)
    #
    # @staticmethod
    # def storage_info() -> StorageInfo:
    #     return StorageInfo(
    #         'console-log',
    #         Console
    #     )
#
#
# class ConsoleLog(list):
#
#     def bulk(self) -> CollectionCrud:
#         return CollectionCrud("console-log", self)
