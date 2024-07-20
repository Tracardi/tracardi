import asyncio
import elasticsearch

from typing import List, Optional, Dict
from pydantic import BaseModel

from tracardi.domain import ExtraInfo
from tracardi.service.license import License, MULTI_TENANT
from tracardi.service.singleton import Singleton
from tracardi.service.storage.elastic.driver.elastic_client import ElasticClient
from tracardi.config import tracardi, mysql
from tracardi.context import ServerContext, get_context, Context
from tracardi.exceptions.log_handler import get_installation_logger
from tracardi.service import system
from tracardi.service.storage.index import Resource

from tracardi.service.storage.mysql.service.database_service import DatabaseService
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.user_service import UserService


if License.has_license() and License.has_service(MULTI_TENANT):
    from com_tracardi.service.multi_tenant_manager import MultiTenantManager

logger = get_installation_logger(__name__)


async def check_installation() -> dict:
    """
    Returns list of missing and updated indices
    """

    # Check MYSQL database exists

    ds = DatabaseService()

    if not await ds.exists(mysql.mysql_database):
        logger.warning("No MySQL database",
                       exc_info=ExtraInfo.exact(origin="installation", package=__name__))
        return {
            "schema_ok": False,
            "admin_ok": False,
            "form_ok": False,
            "warning": None
        }

    is_schema_ok, indices = await system.is_schema_ok()

    if is_schema_ok is False:
        logger.warning("Incorrect Elastic Schema",
                       exc_info=ExtraInfo.exact(origin="installation", package=__name__))
        return {
            "schema_ok": False,
            "admin_ok": None,
            "form_ok": None,
            "warning": None
        }

    ts = TableService()

    if await ts.exists('user'):
        with ServerContext(get_context().switch_context(False)):
            us = UserService()
            admin_records = await us.load_by_role('admin')
    else:
        admin_records = []

    has_admin_account = len(admin_records) > 0

    if tracardi.multi_tenant and (not is_schema_ok or not has_admin_account):
        if License.has_service(MULTI_TENANT):
            mtm = MultiTenantManager()
            context = get_context()

            logger.info(f"Authorizing `{context.tenant}` for installation at {mtm.auth_endpoint}.")

            try:
                await mtm.authorize(tracardi.multi_tenant_manager_api_key)
            except asyncio.exceptions.TimeoutError:
                message = (f"Authorizing failed for tenant `{context.tenant}`. "
                           f"Could not reach Tenant Management Service.")
                logger.warning(message,
                               exc_info=ExtraInfo.exact(origin="installation", package=__name__))
                return {
                    "schema_ok": False,
                    "admin_ok": False,
                    "form_ok": False,
                    "warning": message
                }

            tenant = await mtm.is_tenant_allowed(context.tenant)
            if not tenant:
                logger.warning(f"Authorizing failed for tenant `{context.tenant}`.",
                               exc_info=ExtraInfo.exact(origin="installation", package=__name__))
                return {
                    "schema_ok": False,
                    "admin_ok": False,
                    "form_ok": False,
                    "warning": f"Tenant [{context.tenant}] not allowed."
                }

    return {
        "schema_ok": is_schema_ok,
        "admin_ok": has_admin_account,
        "form_ok": True,
        "warning": None
    }


class SystemInstallationStatus(BaseModel):
    schema_ok: bool = False
    admin_ok: Optional[bool] = None
    form_ok: Optional[bool] = None
    warning: Optional[List[str]] = None
    config: Optional[dict] = {}

    @staticmethod
    async def check() -> 'SystemInstallationStatus':
        status = await check_installation()
        return SystemInstallationStatus(**status)


class InstallationStatus(metaclass=Singleton):
    _installed_tenants: Dict[str, bool] = {}

    def __init__(self):
        self.es = ElasticClient.instance()

    @staticmethod
    async def get_status():
        status = await SystemInstallationStatus.check()
        return {
            "schema": status.schema_ok,
            "users": status.admin_ok,
            "form": status.form_ok
        }

    async def has_logs_index(self, context: Context):
        indices = Resource()
        template = indices.get_template_name('log')

        tenant = context.tenant
        if tenant not in self._installed_tenants or self._installed_tenants[tenant] is False:
            try:
                self._installed_tenants[tenant] = await self.es.exists_index_template(template)
            except elasticsearch.exceptions.ConnectionError:
                return False
        return self._installed_tenants[tenant]


installation_status = InstallationStatus()
