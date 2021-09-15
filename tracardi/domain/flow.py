import uuid
from tracardi_graph_runner.domain.flow import Flow as GraphFlow
from .named_entity import NamedEntity
from .value_object.storage_info import StorageInfo
from typing import Optional, List
from pydantic import BaseModel
from tracardi_graph_runner.domain.flow_graph_data import FlowGraphData, Edge, Position, Node, EdgeBundle
from tracardi_plugin_sdk.domain.register import MetaData, Plugin, Spec
from ..service.secrets import decrypt, encrypt
import logging

logger = logging.getLogger("Flow")
logger.setLevel(logging.WARNING)


class Flow(GraphFlow):
    projects: Optional[List[str]] = ["General"]
    draft: Optional[str] = ""
    lock: bool = False

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'flow',
            FlowRecord
        )

    def encode(self) -> 'FlowRecord':
        return FlowRecord.encode(self)

    def encode_draft(self, draft: 'Flow'):
        self.draft = encrypt(draft.dict())

    def decode_draft(self) -> 'Flow':
        flow = decrypt(self.draft)
        return Flow.construct(_fields_set=self.__fields_set__, **flow)

    @staticmethod
    def new(id: str = None) -> 'Flow':
        return Flow(
            id=str(uuid.uuid4()) if id is None else id,
            name="Empty",
            enabled=False,
            flowGraph=FlowGraphData(nodes=[], edges=[])
        )

    @staticmethod
    def build(name: str, description: str = None, enabled=True, id=None) -> 'Flow':
        return Flow(
            id=str(uuid.uuid4()) if id is None else id,
            name=name,
            description=description,
            enabled=enabled,
            flowGraph=FlowGraphData(
                nodes=[],
                edges=[]
            )
        )

    def __add__(self, edge_bundle: EdgeBundle):
        if edge_bundle.source not in self.flowGraph.nodes:
            self.flowGraph.nodes.append(edge_bundle.source)
        if edge_bundle.target not in self.flowGraph.nodes:
            self.flowGraph.nodes.append(edge_bundle.target)

        if edge_bundle.edge not in self.flowGraph.edges:
            self.flowGraph.edges.append(edge_bundle.edge)
        else:
            logger.warning("Edge {}->{} already exists".format(edge_bundle.edge.source, edge_bundle.edge.target))

        return self


class SpecRecord(BaseModel):
    className: str
    module: str
    inputs: Optional[List[str]] = []
    outputs: Optional[List[str]] = []
    init: Optional[str] = ""
    manual: Optional[str] = None
    author: Optional[str] = None
    license: Optional[str] = "MIT"
    version: Optional[str] = '0.0.1'

    @staticmethod
    def encode(spec: Spec) -> 'SpecRecord':
        return SpecRecord(
            className=spec.className,
            module=spec.module,
            inputs=spec.inputs,
            outputs=spec.outputs,
            init=encrypt(spec.init),
            manual=spec.manual,
            author=spec.author,
            license=spec.license,
            version=spec.version
        )

    def decode(self) -> Spec:
        return Spec(
            className=self.className,
            module=self.module,
            inputs=self.inputs,
            outputs=self.outputs,
            init=decrypt(self.init),
            manual=self.manual,
            author=self.author,
            license=self.license,
            version=self.version
        )


class PluginRecord(BaseModel):
    start: bool = False
    debug: bool = False
    spec: SpecRecord
    metadata: MetaData

    @staticmethod
    def encode(plugin: Plugin) -> 'PluginRecord':
        return PluginRecord(
            start=plugin.start,
            debug=plugin.debug,
            spec=SpecRecord.encode(plugin.spec),
            metadata=plugin.metadata
        )

    def decode(self) -> Plugin:
        data = {
            "start": self.start,
            "debug": self.debug,
            "spec": self.spec.decode(),
            "metadata": self.metadata
        }
        return Plugin.construct(_fields_set=self.__fields_set__, **data)


class NodeRecord(BaseModel):
    id: str
    type: str
    position: Position
    data: PluginRecord

    @staticmethod
    def encode(node: Node):
        return NodeRecord(
            id=node.id,
            type=node.type,
            position=node.position,
            data=PluginRecord.encode(node.data)
        )

    def decode(self) -> Node:
        data = {
            "id": self.id,
            "type": self.type,
            "data": self.data.decode(),
            "position": self.position
        }
        return Node.construct(_fields_set=self.__fields_set__, **data)


class FlowGraphDataRecord(BaseModel):
    nodes: List[NodeRecord]
    edges: List[Edge]

    @staticmethod
    def encode(flowGraph: FlowGraphData) -> 'FlowGraphDataRecord':
        if flowGraph:
            return FlowGraphDataRecord(
                edges=flowGraph.edges,
                nodes=[NodeRecord.encode(node) for node in flowGraph.nodes]
            )

        return FlowGraphDataRecord(
            edges=[],
            nodes=[]
        )

    def decode(self) -> FlowGraphData:
        data = {
            "edges": self.edges,
            "nodes": [node.decode() for node in self.nodes],
        }
        return FlowGraphData.construct(_fields_set=self.__fields_set__, **data)


class FlowRecord(NamedEntity):
    description: Optional[str] = None
    flowGraph: Optional[FlowGraphDataRecord] = None
    enabled: Optional[bool] = True
    projects: Optional[List[str]] = ["General"]
    draft: Optional[str] = ''
    lock: bool = False

    # Persistence

    # def storage(self) -> StorageCrud:
    #     return StorageCrud("flow", FlowRecord, entity=self)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'flow',
            FlowRecord
        )

    @staticmethod
    def encode(flow: Flow) -> 'FlowRecord':
        return FlowRecord(
            id=flow.id,
            description=flow.description,
            name=flow.name,
            enabled=flow.enabled,
            flowGraph=FlowGraphDataRecord.encode(flow.flowGraph),
            projects=flow.projects,
            draft=flow.draft,
            lock=flow.lock

        )

    def decode(self) -> Flow:
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "projects": self.projects,
            "draft": self.draft,
            "lock": self.lock,
            "flowGraph": self.flowGraph.decode() if self.flowGraph else None,
        }
        return Flow.construct(_fields_set=self.__fields_set__, **data)

    def decode_draft(self) -> 'Flow':
        flow = decrypt(self.draft)
        return Flow(**flow)

    def encode_draft(self, draft: 'Flow'):
        self.draft = encrypt(draft.dict())
