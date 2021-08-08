# from typing import Optional, List
# from pydantic import BaseModel
# from tracardi_graph_runner.domain.flow_graph_data import FlowGraphData, Edge, Position, Node
# from tracardi_plugin_sdk.domain.register import MetaData, Plugin, Spec
# from tracardi.service.storage.crud import StorageCrud
# from ..flow import Flow
# from ..named_entity import NamedEntity
# from ...service.secrets import encrypt, decrypt
#
#
# class SpecRecord(BaseModel):
#     className: str
#     module: str
#     inputs: Optional[List[str]] = []
#     outputs: Optional[List[str]] = []
#     init: Optional[str] = ""
#     manual: Optional[str] = None
#
#     @staticmethod
#     def encode(spec: Spec) -> 'SpecRecord':
#         return SpecRecord(
#             className=spec.className,
#             module=spec.module,
#             inputs=spec.inputs,
#             outputs=spec.outputs,
#             init=encrypt(spec.init),
#             manual=spec.manual
#         )
#
#     def decode(self) -> Spec:
#         return Spec(
#             className=self.className,
#             module=self.module,
#             inputs=self.inputs,
#             outputs=self.outputs,
#             init=decrypt(self.init),
#             manual=self.manual
#         )
#
#
# class PluginRecord(BaseModel):
#     start: bool = False
#     debug: bool = False
#     spec: SpecRecord
#     metadata: MetaData
#
#     @staticmethod
#     def encode(plugin: Plugin) -> 'PluginRecord':
#         return PluginRecord(
#             start=plugin.start,
#             debug=plugin.debug,
#             spec=SpecRecord.encode(plugin.spec),
#             metadata=plugin.metadata
#         )
#
#     def decode(self) -> Plugin:
#         data = {
#             "start": self.start,
#             "debug": self.debug,
#             "spec": self.spec.decode(),
#             "metadata": self.metadata
#         }
#         return Plugin.construct(_fields_set=self.__fields_set__, **data)
#
#
# class NodeRecord(BaseModel):
#     id: str
#     type: str
#     position: Position
#     data: PluginRecord
#
#     @staticmethod
#     def encode(node: Node):
#         return NodeRecord(
#             id=node.id,
#             type=node.type,
#             position=node.position,
#             data=PluginRecord.encode(node.data)
#         )
#
#     def decode(self) -> Node:
#         data = {
#             "id": self.id,
#             "type": self.type,
#             "data": self.data.decode(),
#             "position": self.position
#         }
#         return Node.construct(_fields_set=self.__fields_set__, **data)
#
#
# class FlowGraphDataRecord(BaseModel):
#     nodes: List[NodeRecord]
#     edges: List[Edge]
#
#     @staticmethod
#     def encode(flowGraph: FlowGraphData) -> 'FlowGraphDataRecord':
#         return FlowGraphDataRecord(
#             edges=flowGraph.edges,
#             nodes=[NodeRecord.encode(node) for node in flowGraph.nodes]
#         )
#
#     def decode(self) -> FlowGraphData:
#         data = {
#             "edges": self.edges,
#             "nodes": [node.decode() for node in self.nodes],
#         }
#         return FlowGraphData.construct(_fields_set=self.__fields_set__, **data)
#
#
# class FlowRecord(NamedEntity):
#     description: Optional[str] = None
#     flowGraph: Optional[FlowGraphDataRecord] = None
#     enabled: Optional[bool] = True
#     projects: Optional[List[str]] = ["General"]
#
#     # Persistence
#
#     def storage(self) -> StorageCrud:
#         return StorageCrud("flow", FlowRecord, entity=self)
#
#     @staticmethod
#     def encode(flow: Flow) -> 'FlowRecord':
#         return FlowRecord(
#             id=flow.id,
#             description=flow.description,
#             name=flow.name,
#             enabled=flow.enabled,
#             flowGraph=FlowGraphDataRecord.encode(flow.flowGraph),
#             projects=flow.projects
#
#         )
#
#     def decode(self) -> Flow:
#         data = {
#             "id": self.id,
#             "name": self.name,
#             "description": self.description,
#             "enabled": self.enabled,
#             "projects": self.projects,
#             "flowGraph": self.flowGraph.decode() if self.flowGraph else None,
#         }
#         return Flow.construct(_fields_set=self.__fields_set__, **data)
