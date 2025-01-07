from uuid import uuid4

from tracardi.service.license import License, LICENSE
from tracardi.service.setup.setup_bridges import os_default_bridges
from tracardi.service.storage.mysql.service.bridge_service import BridgeService
from tracardi.service.storage.mysql.service.database_service import DatabaseService
from tracardi.service.storage.mysql.service.user_service import UserService
from tracardi.service.storage.mysql.service.version_service import VersionService
from tracardi.context import ServerContext, get_context
from tracardi.domain.credentials import Credentials
from tracardi.domain.user import User
from .logging.logger import get_logger

if License.has_license():
    from com_tracardi.db.bootstrap.default_bridges import commercial_default_bridges

logger = get_logger(__name__)


class MetaDataInstallAdapter:

    async def install_mysql_database(self, credentials: Credentials, version):
        ds = DatabaseService()
        await ds.bootstrap()

        # Install global default bridges
        await BridgeService.bootstrap(default_bridges=os_default_bridges)
        if License.has_service(LICENSE):
            await BridgeService.bootstrap(default_bridges=commercial_default_bridges)

        # TODO content may not be needed - check
        # Install staging
        with ServerContext(get_context().switch_context(production=False)):

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

                # Install version in Mysql

                vs = VersionService()
                await vs.upsert(version)

                # Add admin
                us = UserService()
                await us.insert_if_none(user)

                return True

            else:
                logger.warning("There is at least one admin account. New admin account not created.")
                return True
