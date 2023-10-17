from tracardi.service.wf.domain.flow_graph_data import Edge
from tracardi.service.wf.utils.flow_graph_converter import FlowGraphConverter


def test_convert_valid_flow_to_dag_graph():
    flow = {
        "nodes": [
            {
                "id": "1",
                "type": "node",
                "position": {"x": 100, "y": 100},
                "data": {
                    "metadata": {"name": "Node 1"},
                    "start": True,
                    "debug": False,
                    "spec": {
                        "className": "NodeClass",
                        "module": "NodeModule",
                        "inputs": ["input1"],
                        "outputs": ["output1"],
                        "init": {},
                        "microservice": None
                    }
                }
            },
            {
                "id": "2",
                "type": "node",
                "position": {"x": 200, "y": 200},
                "data": {
                    "metadata": {"name": "Node 2"},
                    "start": False,
                    "debug": True,
                    "spec": {
                        "className": "NodeClass",
                        "module": "NodeModule",
                        "inputs": ["input1"],
                        "outputs": ["output1"],
                        "init": {},
                        "microservice": None
                    }
                }
            }
        ],
        "edges": [
            Edge(**{
                "id": "1",
                "source": "src1",
                "target": "src2",
                "enabled": True,
                "sourceHandle": 'abc',
                "targetHandle": "dfe",
                "type": "ok",
                "data": {}
            }).model_dump()

        ]
    }
    converter = FlowGraphConverter(flow)
    dag_graph = converter.convert_to_dag_graph()
    assert len(dag_graph.nodes) == 2
    assert len(dag_graph.edges) == 1
