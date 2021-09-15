# from typing import Optional, List
#
# from pydantic import BaseModel
#
# from tracardi.domain.entity import Entity
# from tracardi.domain.value_object.storage_info import StorageInfo
# from tracardi.service.storage.crud import StorageCrud
#
#
# class ResponseItem(BaseModel):
#     index: str
#     slices: Optional[List[str]] = None
#
#
# class Response(Entity):
#     data: List[ResponseItem]
#
#     def storage(self) -> StorageCrud:
#         return StorageCrud("response", Response, entity=self)
#
#     @staticmethod
#     def storage_info() -> StorageInfo:
#         return StorageInfo(
#             'response',
#             Response
#         )
