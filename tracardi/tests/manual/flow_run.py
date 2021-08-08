import asyncio

from tracardi_graph_runner.utils.flow_graph_converter import FlowGraphConverter
from tracardi_graph_runner.utils.dag_processor import DagProcessor

from tracardi.domain.context import Context
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session

flow = {
    "nodes": [
        {
            "id": "start",
            "type": "flowNode",
            "position": {
                "x": 380,
                "y": -260
            },
            "data": {
                "start": True,
                "metadata": {
                    "name": "Start",
                    "type": "flowNode",
                    "desc": "Get payload",
                    "width": 100,
                    "height": 100,
                    "icon": "payload"
                },
                "spec": {
                    "className": "PayloadPlugin",
                    "module": "tracardi.tests.manual.plugins.payload.payload_plugin",
                    "inputs": [],
                    "outputs": [
                        "payload"
                    ]
                }
            }
        },
        {
            "id": "763cbc92-5236-4d30-bff2-a10dbbf8c83f",
            "type": "flowNode",
            "position": {
                "x": 380,
                "y": -60
            },
            "data": {
                "metadata": {
                    "name": "Log",
                    "type": "flowNode",
                    "width": 200,
                    "height": 100,
                    "icon": "debug"
                },
                "spec": {
                    "className": "DebugPlugin",
                    "module": "tracardi.tests.manual.plugins.debug.debug_plugin",
                    "inputs": [
                        "payload"
                    ],
                    "outputs": []
                }
            }
        }
    ],
    "edges": [
        {
            "source": "start",
            "sourceHandle": "payload",
            "target": "763cbc92-5236-4d30-bff2-a10dbbf8c83f",
            "targetHandle": "payload",
            "id": "reactflow__edge-9f95ad82-9d7c-4f61-a439-580ba4c730e3payload-763cbc92-5236-4d30-bff2-a10dbbf8c83fpayload",
            "type": "default"
        }
    ]
}

converter = FlowGraphConverter(flow)
x = converter.convert_to_dag_graph()
print(x)
dag = DagProcessor(x)
exec_dag = dag.make_execution_dag()
# print(exec_dag.data)
print()
print(exec_dag.serialize())
print()
# exit()
event = Event(
    id="event-id",
    source=Entity(id="1"),
    session=Entity(id="2"),
    context=Context(),
    type="xxx"
)
session = Session(id="session-id")
profile = Profile(id="profile-id")
init = exec_dag.init(event, session, profile)
asyncio.run(exec_dag.run({}, "flow-1", "event-1"))

