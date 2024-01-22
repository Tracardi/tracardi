import logging

from sqlalchemy import or_

from tracardi.config import tracardi
from tracardi.domain.segment import Segment
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.segment_mapping import map_to_segment_table
from tracardi.service.storage.mysql.schema.table import SegmentTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class SegmentService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        if search:
            where = where_tenant_context(
                SegmentTable,  # Adjusted for Segment
                SegmentTable.name.like(f'%{search}%')
            )
        else:
            where = where_tenant_context(SegmentTable)

        return await self._select_query(SegmentTable,
                                        where=where,
                                        order_by=SegmentTable.name,
                                        limit=limit,
                                        offset=offset)

    async def load_by_id(self, plugin_id: str) -> SelectResult:
        return await self._load_by_id(SegmentTable, primary_id=plugin_id)

    async def delete_by_id(self, segment_id: str) -> str:  # Adjusted for Segment
        return await self._delete_by_id(SegmentTable, primary_id=segment_id)

    async def insert(self, segment: Segment):  # Adjusted for Segment
        return await self._replace(SegmentTable, map_to_segment_table(segment))


    async def load_enabled(self, only_enabled: bool = True):
        where = where_tenant_context(
            SegmentTable,
            SegmentTable.enabled == only_enabled
        )

        return await self._select_query(SegmentTable,
                                        where=where,
                                        order_by=SegmentTable.name)

    async def load_by_event_type(self, event_type, limit:int=500):
        clause = or_(SegmentTable.event_type == event_type, SegmentTable.event_type.is_(None))
        where = where_tenant_context(
                SegmentTable,
                clause
            )

        return await self._select_query(SegmentTable,
                                        where=where,
                                        limit=limit)
