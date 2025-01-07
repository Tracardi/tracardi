from adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from adapter.bigdata.elastic.elastic_apm_adapter import ElasticApmAdapter
from adapter.bigdata.elastic.elastic_collector_adapter import ElasticCollectorAdapter
from adapter.bigdata.elastic.elastic_crud_event_adapter import ElasticCrudEventAdapter
from adapter.bigdata.elastic.elastic_crud_profile_adapter import ElasticCrudProfileAdapter
from adapter.bigdata.elastic.elastic_entity_adapter import ElasticEntityAdapter
from adapter.bigdata.elastic.elastic_gui_adapter import ElasticGuiAdapter
from adapter.bigdata.elastic.elastic_install_adapter import ElasticInstallAdapter
from adapter.bigdata.elastic.elastic_log_adapter import ElasticLogAdapter
from adapter.bigdata.elastic.elastic_gui_search_adapter import ElasticSearchAdapter
from adapter.bigdata.elastic.elastic_analytics_adapter import ElasticAnalyticsAdapter
from adapter.bigdata.elastic.elastic_plugin_adapter import ElasticPluginAdapter
from adapter.bigdata.elastic.elastic_raw_adapter import ElasticRawAdapter
from adapter.bigdata.elastic.elastic_session_adapter import ElasticSessionAdapter

bd_elastic_adapter = ElasticAdapter()
bd_collector_adapter = ElasticCollectorAdapter()
bd_apm_adapter = ElasticApmAdapter()
bd_search_adapter = ElasticSearchAdapter()
bd_log_adapter = ElasticLogAdapter()
bd_analytics_adapter = ElasticAnalyticsAdapter()
bd_plugin_adapter= ElasticPluginAdapter()
bd_gui_adapter =  ElasticGuiAdapter()
bd_crud_profile_adapter = ElasticCrudProfileAdapter()
bd_crud_event_adapter = ElasticCrudEventAdapter()
bd_session_adapter = ElasticSessionAdapter()
bd_entity_adapter = ElasticEntityAdapter()
bd_install_adapter = ElasticInstallAdapter()
bd_raw_adapter = ElasticRawAdapter()

