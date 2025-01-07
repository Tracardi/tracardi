from tracardi.service.dependency import *
from tracardi.service.adapter.metadata.adapter_selector import md_install_adapter
from tracardi.domain.credentials import Credentials
from tracardi.common.logging.log_handler import get_installation_logger

logger = get_installation_logger(__name__)


async def install_system(credentials: Credentials):

    staging_install_result, production_install_result = await bd_install_adapter.install_big_data_database(credentials)

    admin = await md_install_adapter.install_mysql_database(credentials)
    staging_install_result['admin'] = admin
    return staging_install_result, production_install_result
