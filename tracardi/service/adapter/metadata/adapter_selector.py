from tracardi.common.decorator.run_once import run_once
from tracardi.config import tracardi
from tracardi.service.adapter.metadata.mysql.mysql_install_adapter import MetaDataInstallAdapter

_meta_data_adapter_var = tracardi.meta_data_adapter


@run_once
def md_install_adapter() -> MetaDataInstallAdapter:
    if _meta_data_adapter_var.lower() == 'mysql':
        return MetaDataInstallAdapter()
    else:
        raise ValueError(f"Unknown metadata install adapter `{_meta_data_adapter_var}`")