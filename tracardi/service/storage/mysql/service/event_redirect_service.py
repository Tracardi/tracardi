import logging
from typing import Tuple, Optional

from tracardi.config import tracardi
from tracardi.domain.event_redirect import EventRedirect
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_redirect_mapping import map_to_event_redirect_table, \
    map_to_event_redirect
from tracardi.service.storage.mysql.schema.table import EventRedirectTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventRedirectService(TableService):

    async def load_all(self, search:str, offset:int=None, limit:int=None) -> SelectResult:
        return await self._load_all_in_deployment_mode(EventRedirectTable, search, limit, offset)

    async def load_by_id(self, event_redirect_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(EventRedirectTable, primary_id=event_redirect_id)

    async def delete_by_id(self, event_redirect_id: str) -> Tuple[bool, Optional[EventRedirect]]:
        return await self._delete_by_id_in_deployment_mode(EventRedirectTable, map_to_event_redirect, primary_id=event_redirect_id)

    async def insert(self, event_redirect: EventRedirect):
        return await self._replace(EventRedirectTable, map_to_event_redirect_table(event_redirect))
