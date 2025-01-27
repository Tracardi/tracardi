from tracardi.config import tracardi
from tracardi.common.decorator.run_once import run_once

_bd_adapter_var = tracardi.big_data_adapter

if _bd_adapter_var == 'elastic':
    from system.adapter.os.bigdata.elastic.elastic_adapter import ElasticAdapter
    from system.adapter.os.bigdata.elastic.elastic_apm_adapter import ElasticApmAdapter
    from system.adapter.os.bigdata.elastic.elastic_entity_adapter import ElasticEntityAdapter
    from system.adapter.os.bigdata.elastic.elastic_event_adapter import ElasticEventAdapter
    from system.adapter.os.bigdata.elastic.elastic_install_adapter import ElasticInstallAdapter
    from system.adapter.os.bigdata.elastic.elastic_log_adapter import ElasticLogAdapter
    from system.adapter.os.bigdata.elastic.elastic_gui_search_adapter import ElasticSearchAdapter
    from system.adapter.os.bigdata.elastic.elastic_profile_adapter import ElasticProfileAdapter
    from system.adapter.os.bigdata.elastic.elastic_raw_adapter import ElasticRawAdapter
    from system.adapter.os.bigdata.elastic.elastic_report_adapter import ElasticReportAdapter
    from system.adapter.os.bigdata.elastic.elastic_session_adapter import ElasticSessionAdapter
elif _bd_adapter_var == 'starrocks':
    pass


@run_once
def bd_install_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticInstallAdapter()

    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter
