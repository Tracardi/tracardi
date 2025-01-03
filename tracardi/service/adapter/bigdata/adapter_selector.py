from tracardi.config import tracardi
from tracardi.common.decorator.run_once import run_once
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_apm_adapter import ElasticApmAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_audience_adapter import ElasticAudienceAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_collector_adapter import ElasticCollectorAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_crud_event_adapter import ElasticCrudEventAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_crud_profile_adapter import ElasticCrudProfileAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_gui_adapter import ElasticGuiAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_log_adapter import ElasticLogAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_gui_search_adapter import ElasticSearchAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_analytics_adapter import ElasticAnalyticsAdapter
from tracardi.service.adapter.bigdata.elastic.elastic_plugin_adapter import ElasticPluginAdapter

_big_data_adapter_var = tracardi.big_data_adapter


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


@run_once
def bd_analytics_adapter() -> ElasticAnalyticsAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticAnalyticsAdapter()
    else:
        raise ValueError(f"Unknown big analytics adapter `{_big_data_adapter_var}`")


@run_once
def bd_plugin_adapter() -> ElasticPluginAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticPluginAdapter()
    else:
        raise ValueError(f"Unknown big plugin adapter `{_big_data_adapter_var}`")


@run_once
def bd_gui_adapter() -> ElasticGuiAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticGuiAdapter()
    else:
        raise ValueError(f"Unknown big data GUI adapter `{_big_data_adapter_var}`")


@run_once
def bd_audience_adapter() -> ElasticAudienceAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticAudienceAdapter()
    else:
        raise ValueError(f"Unknown big data audience adapter `{_big_data_adapter_var}`")


@run_once
def bd_crud_profile_adapter() -> ElasticCrudProfileAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticCrudProfileAdapter()
    else:
        raise ValueError(f"Unknown big data profile CRUD adapter `{_big_data_adapter_var}`")


@run_once
def bd_crud_event_adapter() -> ElasticCrudEventAdapter:
    if _big_data_adapter_var.lower() == 'elastic':
        return ElasticCrudEventAdapter()
    else:
        raise ValueError(f"Unknown big data event CRUD adapter `{_big_data_adapter_var}`")
