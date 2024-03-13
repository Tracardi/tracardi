# import logging
# from typing import Optional, Tuple
#
# from sqlalchemy import or_
#
# from tracardi.config import tracardi
# from tracardi.domain.segment import Segment
# from tracardi.exceptions.log_handler import log_handler
# from tracardi.service.storage.mysql.mapping.segment_mapping import map_to_segment_table, map_to_segment
# from tracardi.service.storage.mysql.schema.table import SegmentTable
# from tracardi.service.storage.mysql.utils.select_result import SelectResult
# from tracardi.service.storage.mysql.service.table_service import TableService
# from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context
#
# logger = logging.getLogger(__name__)
# logger.setLevel(tracardi.logging_level)
# logger.addHandler(log_handler)
#
#
# # TODO remove after the post event segmentation, and segmentation_endpoint  is removed
# class SegmentService(TableService):
#
#     async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
#         return await self._load_all_in_deployment_mode(SegmentTable, search, limit, offset)
#
#     async def load_by_id(self, plugin_id: str) -> SelectResult:
#         return await self._load_by_id_in_deployment_mode(SegmentTable, primary_id=plugin_id)
#
#     async def delete_by_id(self, segment_id: str) -> Tuple[bool, Optional[Segment]]:
#         return await self._delete_by_id_in_deployment_mode(SegmentTable, map_to_segment,
#                                                            primary_id=segment_id)
#
#     async def insert(self, segment: Segment):
#         return await self._replace(SegmentTable, map_to_segment_table(segment))
#
#
#     async def load_enabled(self, only_enabled: bool = True):
#         where = where_tenant_and_mode_context(
#             SegmentTable,
#             SegmentTable.enabled == only_enabled
#         )
#
#         return await self._select_in_deployment_mode(
#             SegmentTable,
#             where=where,
#             order_by=SegmentTable.name)
#
