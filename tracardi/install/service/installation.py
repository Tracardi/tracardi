from tracardi.domain.credentials import Credentials
from tracardi.common.logging.log_handler import get_installation_logger
from tracardi.config import tracardi
from tracardi.service.dependency.adapters.big_data_adapter import bd_install_adapter

logger = get_installation_logger(__name__)
_bd_install_adapter = bd_install_adapter()

async def install_system(credentials: Credentials):
    admin = await md_install_adapter.install_mysql_database(credentials, version=tracardi.version)
    staging_install_result, production_install_result = await _bd_install_adapter.install_big_data_database(credentials)

    staging_install_result['admin'] = admin
    return staging_install_result, production_install_result
