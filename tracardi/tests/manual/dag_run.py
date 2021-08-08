import asyncio

from tracardi_graph_runner.domain.dag_graph import DagGraph
from tracardi_graph_runner.utils.dag_processor import DagProcessor


data = {
    "nodes": [
        {"id": "n1", "outputs": ["TRUE", "FALSE"], "inputs": [], "className": "task1",
         "module": 'tracardi.tests.manual.plugins.plugins', "init": {"condition": "abc"}},

        {"id": "n2", "outputs": ["NODE2_o"], "inputs": ["NODE2_i"], "className": "task2",
         "module": 'tracardi.tests.manual.plugins.plugins'},

        {"id": "n3", "outputs": ['NODE3_o'], "inputs": ["NODE3_i"], "className": "task3",
         "module": 'tracardi.tests.manual.plugins.plugins'},
        {"id": "n4", "outputs": ["NODE4_o"], "inputs": ["NODE4_2_i", "NODE4_3_i", "NODE4_1_i"], "className": "task4",
         "module": 'tracardi.tests.manual.plugins.plugins'},
        {"id": "n5", "outputs": ["NODE5_i"], "inputs": [], "className": "task5", "module": 'tracardi.tests.manual.plugins.plugins'}

    ],

    'edges': [
        {"id": "e1", "source": {"node_id": "n1", "param": "TRUE"}, "target": {"node_id": "n2", "param": "NODE2_i"}},
        {"id": "e2", "source": {"node_id": "n1", "param": "FALSE"}, "target": {"node_id": "n3", "param": "NODE3_i"}},
        {"id": "e3", "source": {"node_id": "n2", "param": "NODE2_o"},
         "target": {"node_id": "n4", "param": "NODE4_2_i"}},
        {"id": "e4", "source": {"node_id": "n3", "param": "NODE3_o"},
         "target": {"node_id": "n4", "param": "NODE4_3_i"}},
        {"id": "e5", "source": {"node_id": "n1", "param": "TRUE"}, "target": {"node_id": "n4", "param": "NODE4_1_i"}},
        {"id": "e6", "source": {"node_id": "n4", "param": "NODE4_o"}, "target": {"node_id": "n5", "param": "NODE5_i"}},
    ]
}
flow = DagGraph(**data)
dag = DagProcessor(flow)
exec_dag = dag.make_execution_dag(start_node_ids=["n1"])
# print(exec_dag.data)
print()
print(exec_dag.serialize())
print()
# exit()
exec_dag.init()
asyncio.run(exec_dag.run({}))
