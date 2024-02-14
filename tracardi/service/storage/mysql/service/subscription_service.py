import logging

from typing import Tuple, Optional

from tracardi.config import tracardi
from tracardi.domain.subscription import Subscription
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.subscription_mapping import map_to_subscription_table, map_to_subscription
from tracardi.service.storage.mysql.schema.table import SubscriptionTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class SubscriptionService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(SubscriptionTable, search, limit, offset)

    async def load_by_id(self, subscription_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(SubscriptionTable, primary_id=subscription_id)

    async def delete_by_id(self, subscription_id: str) -> Tuple[bool, Optional[Subscription]]:
        return await self._delete_by_id_in_deployment_mode(SubscriptionTable, map_to_subscription,
                                                           primary_id=subscription_id)

    async def insert(self, subscription: Subscription):
        return await self._replace(SubscriptionTable, map_to_subscription_table(subscription))

