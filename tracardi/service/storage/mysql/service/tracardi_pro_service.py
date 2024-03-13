import logging
from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.schema.table import TracardiProTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class TracardiProService(TableService):

    def _get_id(self) -> str:
        return get_context().tenant

    async def load_by_tenant_id(self) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(TracardiProTable, primary_id=self._get_id())


    async def authorize(self, token: str) -> bool:
        record = await self.load_by_tenant_id()
        return record.exists() and record.rows.token == token

    async def insert(self, token: str):
        record = await self.load_by_tenant_id()
        if not record.exists():
            context = get_context()
            table = TracardiProTable(
                id=self._get_id(),
                token=token,
                tenant=context.tenant,
                production=context.production
            )
            return await self._insert(table)

    async def upsert(self, token: str):
        context = get_context()
        table = TracardiProTable(
            id=self._get_id(),
            token=token,
            tenant=context.tenant,
            production=context.production
        )
        return await self._replace(TracardiProTable,table)