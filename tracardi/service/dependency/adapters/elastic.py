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

bd_elastic_adapter = ElasticAdapter()
bd_apm_adapter = ElasticApmAdapter()
bd_search_adapter = ElasticSearchAdapter()
bd_log_adapter = ElasticLogAdapter()
bd_install_adapter = ElasticInstallAdapter()
bd_entity_adapter = ElasticEntityAdapter()
bd_raw_adapter = ElasticRawAdapter()
bd_session_adapter = ElasticSessionAdapter()
bd_event_adapter = ElasticEventAdapter()
bd_profile_adapter = ElasticProfileAdapter()
bd_report_adapter = ElasticReportAdapter()

