import asyncio
import logging
import os
from uuid import uuid4

from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.license import License, MULTI_TENANT, LICENSE
from tracardi.service.storage.mysql.bootstrap.bridge import os_default_bridges
from tracardi.service.storage.mysql.service.bridge_service import BridgeService
from tracardi.service.storage.mysql.service.database_service import DatabaseService
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.user_service import UserService
from tracardi.service.tracker import track_event
from tracardi.config import tracardi, elastic, mysql
from tracardi.context import ServerContext, get_context
from tracardi.domain.credentials import Credentials
from tracardi.domain.user import User
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.fake_data_maker.generate_payload import generate_payload
from tracardi.service.plugin.plugin_install import install_default_plugins
from tracardi.service.setup.setup_indices import create_schema, run_on_start
from tracardi.service.storage.driver.elastic import raw as raw_db
from tracardi.service.storage.driver.elastic import system as system_db
from tracardi.service.storage.index import Resource

if License.has_license():
    from com_tracardi.db.bootstrap.default_bridges import commercial_default_bridges
    if License.has_service(MULTI_TENANT):
        from com_tracardi.service.multi_tenant_manager import MultiTenantManager


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def check_installation():
    """
    Returns list of missing and updated indices
    """

    # Check MYSQL database exists

    ds = DatabaseService()

    if not await ds.exists(mysql.mysql_database):
        return {
            "schema_ok": False,
            "admin_ok": False,
            "form_ok": False,
            "warning": None
        }

    is_schema_ok, indices = await system_db.is_schema_ok()

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


async def install_system(credentials: Credentials):
    if tracardi.multi_tenant:
        if not License.has_license():
            raise PermissionError("Installation forbidden. Multi-tenant installation is not "
                                  "allowed in open-source version.")
        if not License.has_service(MULTI_TENANT):
            raise PermissionError("Installation forbidden. Multi-tenant installation is not "
                                  "included in your license.")
        context = get_context()
        mtm = MultiTenantManager()
        logger.info(f"Authorizing `{context.tenant}` for installation at {mtm.auth_endpoint}.")

        await mtm.authorize(tracardi.multi_tenant_manager_api_key)
        tenant = await mtm.is_tenant_allowed(context.tenant)
        if not tenant:
            raise PermissionError(f"Installation forbidden. Tenant [{context.tenant}] not allowed.")

        if tenant.install_token and tenant.install_token != credentials.token:
            raise PermissionError("Installation forbidden. Invalid installation token.")

        logger.info(f"Tenant `{context.tenant}` authorized for installation.")

    else:
        if tracardi.installation_token and tracardi.installation_token != credentials.token:
            raise PermissionError("Installation forbidden. Invalid installation token.")

    info = await raw_db.health()

    if 'number_of_data_nodes' in info and int(info['number_of_data_nodes']) == 1:
        os.environ['ELASTIC_INDEX_REPLICAS'] = "0"
        elastic.replicas = "0"
        logger.warning("Elasticsearch replicas decreased to 0 due to only one data node in the cluster.")

    if credentials.needs_admin:
        if credentials.empty() or not credentials.username_as_email():
            raise PermissionError("Installation forbidden. Invalid admin account "
                                  "login or password. Login must be a valid email and password "
                                  "can not be empty.")

    # Install defaults

    async def _install():
        schema_result = await create_schema(Resource().get_index_mappings(), credentials.update_mapping)

        await run_on_start()

        return {
            "created": schema_result,
            "admin": False
        }

    # Bootstrap MySQL Database

    ds = DatabaseService()
    await ds.bootstrap()

    # Install global default bridges
    await BridgeService.bootstrap(default_bridges=os_default_bridges)
    if License.has_service(LICENSE):
        await BridgeService.bootstrap(default_bridges=commercial_default_bridges)


    # Install staging
    with ServerContext(get_context().switch_context(production=False)):
        staging_install_result = await _install()

        # Add admin
        us = UserService()
        admins = await us.load_by_role('admin')

        if credentials.needs_admin and len(admins) == 0:
            user = User(
                id=str(uuid4()),
                password=User.encode_password(credentials.password),
                roles=['admin', 'maintainer'],
                email=credentials.username,
                name="Default Admin",
                enabled=True
            )

            us = UserService()

            if await us.insert_if_none(user):
                logger.info("Default admin account created.")

            # if not await user_db.check_if_exists(credentials.username):
            #     await user_db.add_user(user)
            #     logger.info("Default admin account created.")

            staging_install_result['admin'] = True

        else:
            logger.warning("There is at least one admin account. New admin account not created.")
            staging_install_result['admin'] = True

        # Demo
        if os.environ.get("DEMO", 'no') == 'yes':

            # Demo

            for i in range(0, 100):
                payload = generate_payload(source=tracardi.internal_source)

                await track_event(
                    TrackerPayload(**payload),
                    "0.0.0.0",
                    allowed_bridges=['internal', 'rest'])

    # Install production
    with ServerContext(get_context().switch_context(production=True)):
        production_install_result = await _install()

    logger.info(f"Installing plugins on startup")
    installed_plugins = await install_default_plugins()
    staging_install_result['plugins'] = installed_plugins
    production_install_result['plugins'] = installed_plugins

    return staging_install_result, production_install_result
