import asyncio

from typing import List, Optional, Dict
from pydantic import BaseModel

from tracardi.service.license import License, MULTI_TENANT
from tracardi.service.installation import check_installation
from tracardi.service.singleton import Singleton
from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.config import tracardi
from tracardi.context import ServerContext, get_context, Context
from tracardi.exceptions.log_handler import get_installation_logger
from tracardi.service.storage.driver.elastic import system as system_db
from tracardi.service.storage.driver.elastic import user as user_db
from tracardi.service.storage.index import Resource

if License.has_license() and License.has_service(MULTI_TENANT):
    from com_tracardi.service.multi_tenant_manager import MultiTenantManager

logger = get_installation_logger(__name__)


async def check_installation():
    """
    Returns list of missing and updated indices
    """

    is_schema_ok, indices = await system_db.is_schema_ok()

    # Missing admin
    existing_aliases = [idx[1] for idx in indices if idx[0] == 'existing_alias']
    index = Resource().get_index_constant('user')

    with ServerContext(get_context().switch_context(False)):
        if index.get_index_alias() in existing_aliases:
            admins = await user_db.search_by_role('admin')
        else:
            admins = None

    has_admin_account = admins is not None and admins.total > 0

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
                logger.warning(message)
                return {
                    "schema_ok": False,
                    "admin_ok": False,
                    "form_ok": False,
                    "warning": message
                }

            tenant = await mtm.is_tenant_allowed(context.tenant)
            if not tenant:
                logger.warning(f"Authorizing failed for tenant `{context.tenant}`.")
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
    admin_ok: bool = False
    form_ok: bool = False
    warning: Optional[List[str]] = None

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
            self._installed_tenants[tenant] = await self.es.exists_index_template(template)

        return self._installed_tenants[tenant]


installation_status = InstallationStatus()
