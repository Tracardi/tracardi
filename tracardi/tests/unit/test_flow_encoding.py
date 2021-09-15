from tracardi_graph_runner.domain.flow_graph_data import FlowGraphData, Node, Edge
import tracardi.domain.flow as f
from tracardi.domain.flow import FlowRecord


def test_flow_encoding():
    flow = f.Flow(
        id="1",
        enabled=True,
        name="Flow",
        flowGraph=FlowGraphData(
            nodes=[
                Node(**{
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
                            ],
                            'init': {"ala-ma-kota": "a-kot"}
                        }
                    }
                }),
                Node(**{
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
                })
            ],
            edges=[
                Edge(**
                     {
                         "source": "start",
                         "sourceHandle": "payload",
                         "target": "763cbc92-5236-4d30-bff2-a10dbbf8c83f",
                         "targetHandle": "payload",
                         "id": "reactflow__edge-9f95ad82-9d7c-4f61-a439-580ba4c730e3payload-763cbc92-5236-4d30-bff2-a10dbbf8c83fpayload",
                         "type": "default"
                     })
            ]
        )
    )

    record = FlowRecord.encode(flow)
    new_flow = record.decode()
    assert new_flow.flowGraph.nodes[0].data.spec.init == {"ala-ma-kota": "a-kot"}



