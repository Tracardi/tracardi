from tracardi.domain.flow import Flow
from tracardi_graph_runner.domain.edge import Edge
from tracardi_graph_runner.domain.node import Node
from tracardi_graph_runner.service.node_indexer import index_nodes
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class StartAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, payload):
        if self.debug:
            if not self.node.has_input_node(self.flow.flowGraph.nodes, class_name='DebugPayloadAction'):
                raise ValueError("Start action can not run in debug mode without connection to Debug action.")

        return Result(port="payload", value={})


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.start_action',
            className='StartAction',
            inputs=["payload"],
            outputs=["payload"],
            init=None,
            version='0.6.0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Start',
            desc='Starts workflow and returns empty payload.',
            keywords=['start node'],
            icon='start',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns empty payload object.")
                }
            )
        )
    )
