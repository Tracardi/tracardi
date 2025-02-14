from tracardi.config import tracardi
from tracardi.domain.credentials import Credentials
from tracardi.common.logging.log_handler import get_installation_logger
from tracardi.service.dependency.adapters.big_data_adapter import *
from tracardi.service.dependency.adapters.mysql import md_install_adapter
from tracardi.service.plugin.plugin_install import install_default_plugins

logger = get_installation_logger(__name__)


async def install_system(credentials: Credentials):
    admin = await md_install_adapter.install_mysql_database(credentials, version=tracardi.version)
    installed_plugins = await install_default_plugins()

    staging_install_result, production_install_result = await bd_install_adapter.install_big_data_database(credentials)

    staging_install_result['plugins'] = installed_plugins
    production_install_result['plugins'] = installed_plugins

    staging_install_result['admin'] = admin
    return staging_install_result, production_install_result
