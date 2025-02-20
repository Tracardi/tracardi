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
    from system.adapter.os.bigdata.elastic.elastic_internal_adapter import ElasticInternalAdapter
elif _bd_adapter_var == 'starrocks':
    pass


@run_once
def _bd_elastic_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter

@run_once
def _bd_install_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticInstallAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter

@run_once
def _bd_report_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticReportAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter


@run_once
def _bd_raw_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticRawAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter


@run_once
def _bd_log_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticLogAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter


@run_once
def _bd_apm_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticApmAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter

@run_once
def _bd_entity_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticEntityAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter


@run_once
def _bd_search_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticSearchAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter


@run_once
def _bd_event_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticEventAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter


@run_once
def _bd_profile_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticProfileAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter


@run_once
def _bd_session_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticSessionAdapter()
    else:
        raise ValueError(f"Unknown big data adapter `{_bd_adapter_var}`")

    return _bd_adapter


@run_once
def _bd_internal_adapter():
    if _bd_adapter_var.lower() == 'elastic':
        _bd_adapter = ElasticInternalAdapter()
    else:
        raise ValueError(f"Unknown big data internal adapter `{_bd_adapter_var}`")

    return _bd_adapter

bd_elastic_adapter = _bd_elastic_adapter()
bd_install_adapter = _bd_install_adapter()
bd_report_adapter = _bd_report_adapter()
bd_raw_adapter = _bd_raw_adapter()
bd_log_adapter = _bd_log_adapter()
bd_apm_adapter = _bd_apm_adapter()
bd_entity_adapter = _bd_entity_adapter()
bd_event_adapter = _bd_event_adapter()
bd_search_adapter = _bd_search_adapter()
bd_profile_adapter = _bd_profile_adapter()
bd_session_adapter = _bd_session_adapter()
bd_internal_adapter = _bd_internal_adapter()

