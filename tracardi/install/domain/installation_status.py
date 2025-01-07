import asyncio

from typing import List, Optional
from pydantic import BaseModel

from tracardi.domain import ExtraInfo
from tracardi.service.dependency import *
from tracardi.service.license import License
from tracardi.service.license_type import MULTI_TENANT
from tracardi.common.singleton import Singleton
from tracardi.config import tracardi, mysql
from tracardi.context import ServerContext, get_context
from tracardi.common.logging.log_handler import get_installation_logger

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

    ts = TableService()

    if await ts.exists('user'):
        with ServerContext(get_context().switch_context(False)):
            us = UserService()
            admin_records = await us.load_by_role('admin')
    else:
        admin_records = []

    has_admin_account = len(admin_records) > 0

    schema_ok, indices = await bd_install_adapter.is_big_data_schema_ok()

    if schema_ok is False:
        return {
            "schema_ok": False,
            "admin_ok": has_admin_account,
            "form_ok": None,
            "warning": None
        }

    if tracardi.multi_tenant and (not schema_ok or not has_admin_account):
        if License.has_service(MULTI_TENANT):
            mtm = MultiTenantManager()
            context = get_context()

            logger.info(f"Authorizing `{context.tenant}` for installation at {mtm.auth_endpoint}.")

            try:
                await mtm.authorize(tracardi.multi_tenant_manager_api_key)
            except asyncio.exceptions.TimeoutError:
                message = (f"Authorizing failed for tenant `{context.tenant}`. "
                           f"Could not reach Tenant Management Service.")
                logger.warning(message, exc_info=ExtraInfo.exact(origin="installation", package=__name__))
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
        "schema_ok": schema_ok,
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

    @staticmethod
    async def get_status():
        status = await SystemInstallationStatus.check()
        return {
            "schema": status.schema_ok,
            "users": status.admin_ok,
            "form": status.form_ok
        }


installation_status = InstallationStatus()
