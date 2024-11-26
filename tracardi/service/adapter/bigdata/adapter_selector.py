from tracardi.service.adapter.bigdata.elastic.elastic_apm_adapter import ElasticApmAdapter
from com_tracardi.config import com_tracardi_settings

from tracardi.service.decorators.run_once import run_once

_big_data_adapter_var = com_tracardi_settings.big_data_adapter


@run_once
def apm_collector_adapter() -> ElasticApmAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticApmAdapter()
    else:
        raise ValueError(f"Unknown APM adapter `{_big_data_adapter_var}`")
