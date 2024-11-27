from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_apm_adapter import ElasticApmAdapter
from com_tracardi.config import com_tracardi_settings
from tracardi.service.adapter.bigdata.elastic.elastic_collector_adapter import ElasticCollectorAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_log_adapter import ElasticLogAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_gui_search_adapter import ElasticSearchAdapter

from tracardi.service.decorators.run_once import run_once

_big_data_adapter_var = com_tracardi_settings.big_data_adapter


@run_once
def bd_elastic_adapter() -> ElasticAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_big_data_adapter_var}`")


@run_once
def bd_collector_adapter() -> ElasticCollectorAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticCollectorAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_big_data_adapter_var}`")

@run_once
def bd_apm_adapter() -> ElasticApmAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticApmAdapter()
    else:
        raise ValueError(f"Unknown APM adapter `{_big_data_adapter_var}`")


@run_once
def bd_search_adapter() -> ElasticSearchAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticSearchAdapter()
    else:
        raise ValueError(f"Unknown search adapter `{_big_data_adapter_var}`")


@run_once
def bd_log_adapter() -> ElasticLogAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticLogAdapter()
    else:
        raise ValueError(f"Unknown big data log adapter `{_big_data_adapter_var}`")