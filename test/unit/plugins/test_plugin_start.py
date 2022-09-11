from tracardi.domain.flow import Flow
from tracardi.process_engine.action.v1.end_action import EndAction
from tracardi.process_engine.action.v1.increase_views_action import IncreaseViewsAction
from tracardi.process_engine.action.v1.flow.start.start_action import StartAction
from tracardi.domain.profile import Profile
from tracardi.service.plugin.service.plugin_runner import run_plugin
from tracardi.service.wf.service.builders import action
from tracardi.service.wf.utils.dag_processor import DagProcessor
from tracardi.service.wf.utils.flow_graph_converter import FlowGraphConverter
from tracardi.domain.event import Event, EventSession
from tracardi.domain.event_metadata import EventMetadata, EventTime
from tracardi.domain.entity import Entity


def build_some_workflow_with_start_action(debug: bool = False):
    start = action(StartAction)
    increase_views = action(IncreaseViewsAction)
    end = action(EndAction)

    flow = Flow.build("End2End - flow", id="1")
    flow += start('payload') >> increase_views('payload')
    flow += increase_views('payload') >> end('payload')

    converter = FlowGraphConverter(flow.flowGraph.dict())
    dag_graph = converter.convert_to_dag_graph()
    dag = DagProcessor(dag_graph)

    exec_dag = dag.make_execution_dag(debug=debug)
    return flow, exec_dag.graph[1]


def test_plugin_start():
    payload = {}
    init = {
        "debug": False,  # CANNOT TEST
        "event_types": [
            {
                "id": "type-2",
                "name": "type-2"
            }
        ],
        "profile_less": False,
        "session_less": False,
        "properties": "{}",
        "event_id": None,  # CANNOT TEST - REQUIRES DATABASE ACCESS
        "event_type": None  # SAME AS ABOVE
    }
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )

    flow, node = build_some_workflow_with_start_action(True)

    result = run_plugin(StartAction, init, payload, profile=Profile(id="1"), flow=flow,
                        node=node)
    Event(**result.output.value)
    assert result.output.port == 'payload'
