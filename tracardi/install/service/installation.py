from tracardi.service.adapter.bigdata.adapter_selector import bd_elastic_adapter, bd_install_adapter
from tracardi.service.adapter.metadata.adapter_selector import md_install_adapter
from tracardi.domain.credentials import Credentials
from tracardi.common.logging.log_handler import get_installation_logger

logger = get_installation_logger(__name__)
_bd_adapter = bd_elastic_adapter()
_md_install_adapter = md_install_adapter()
_bd_install_adapter = bd_install_adapter()


async def install_system(credentials: Credentials):

    staging_install_result, production_install_result = await _bd_install_adapter.install_big_data_database(credentials)

    admin = await _md_install_adapter.install_mysql_database(credentials)
    staging_install_result['admin'] = admin
    return staging_install_result, production_install_result
