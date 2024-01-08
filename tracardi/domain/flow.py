import uuid
from datetime import datetime

from tracardi.service.wf.domain.flow_graph import FlowGraph
from .named_entity import NamedEntity
from .value_object.storage_info import StorageInfo
from typing import Optional, List, Any
from pydantic import BaseModel
from tracardi.service.wf.domain.flow_graph_data import FlowGraphData, EdgeBundle
from tracardi.service.plugin.domain.register import MetaData, Plugin, Spec, NodeEvents, MicroserviceConfig

from ..config import tracardi
from ..service.secrets import decrypt, encrypt, b64_encoder, b64_decoder
import logging

from ..service.utils.date import now_in_utc

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)


class FlowSchema(BaseModel):
    version: str = tracardi.version.version
    uri: str = 'http://www.tracardi.com/2021/WFSchema'
    server_version: str = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.server_version = tracardi.version.version


class Flow(FlowGraph):
    projects: Optional[List[str]] = ["General"]
    lock: bool = False
    type: str
    timestamp: Optional[datetime] = None
    deploy_timestamp: Optional[datetime] = None
    wf_schema: FlowSchema = FlowSchema()

    def arrange_nodes(self):
        if self.flowGraph is not None:
            targets = {edge.target for edge in self.flowGraph.edges}
            starting_nodes = [node for node in self.flowGraph.nodes if node.id not in targets]

            start_at = [0, 0]
            for starting_node in starting_nodes:
                node_to_distance_map = self.flowGraph.traverse_graph_for_distances(start_at_id=starting_node.id)

                for node_id in node_to_distance_map:
                    node = self.flowGraph.get_node_by_id(node_id)
                    node.position.y = start_at[1] + 150 * node_to_distance_map[node_id]

                distance_to_nodes_map = {}
                for node_id in node_to_distance_map:
                    if node_to_distance_map[node_id] not in distance_to_nodes_map:
                        distance_to_nodes_map[node_to_distance_map[node_id]] = []
                    distance_to_nodes_map[node_to_distance_map[node_id]].append(node_id)

                for node_ids in distance_to_nodes_map.values():
                    nodes = [self.flowGraph.get_node_by_id(node_id) for node_id in node_ids]
                    row_center = start_at[0] - 200 * len(nodes) + 250
                    for node in nodes:
                        node.position.x = row_center - node.data.metadata.width // 2
                        row_center += node.data.metadata.width

                start_at[0] += len(max(distance_to_nodes_map.values(), key=len)) * 200

    def get_production_workflow_record(self) -> 'FlowRecord':

        production = encrypt(self.model_dump())

        return FlowRecord(
            id=self.id,
            timestamp=self.timestamp,
            deploy_timestamp=self.deploy_timestamp,
            description=self.description,
            name=self.name,
            projects=self.projects,
            draft=production,
            production=production,
            lock=self.lock,
            type=self.type
        )

    def get_empty_workflow_record(self, type: str) -> 'FlowRecord':

        return FlowRecord(
            id=self.id,
            timestamp=now_in_utc(),
            description=self.description,
            name=self.name,
            projects=self.projects,
            lock=self.lock,
            type=type
        )

    @staticmethod
    def from_workflow_record(record: 'FlowRecord', output) -> 'Flow':

        if output == 'draft':
            decrypted = decrypt(record.draft)
        else:
            decrypted = decrypt(record.production)

        if 'type' not in decrypted:
            decrypted['type'] = record.type

        flow = Flow(**decrypted)
        flow.deploy_timestamp = record.deploy_timestamp
        flow.timestamp = record.timestamp

        if not flow.timestamp:
            flow.timestamp = now_in_utc()

        return flow

    @staticmethod
    def new(id: str = None) -> 'Flow':
        return Flow(
            id=str(uuid.uuid4()) if id is None else id,
            timestamp=now_in_utc(),
            name="Empty",
            wf_schema=FlowSchema(version=str(tracardi.version)),
            flowGraph=FlowGraphData(nodes=[], edges=[]),
            type='collection'
        )

    @staticmethod
    def build(name: str, description: str = None, id=None, lock=False, projects=None, type='collection') -> 'Flow':
        if projects is None:
            projects = ["General"]

        return Flow(
            id=str(uuid.uuid4()) if id is None else id,
            timestamp=now_in_utc(),
            name=name,
            wf_schema=FlowSchema(version=str(tracardi.version)),
            description=description,
            projects=projects,
            lock=lock,
            flowGraph=FlowGraphData(
                nodes=[],
                edges=[]
            ),
            type=type
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
    id: str
    className: str
    module: str
    inputs: Optional[List[str]] = []
    outputs: Optional[List[str]] = []
    init: Optional[str] = ""
    microservice: Optional[MicroserviceConfig] = None
    node: Optional[NodeEvents] = None
    form: Optional[str] = ""
    manual: Optional[str] = None
    author: Optional[str] = None
    license: Optional[str] = "MIT"
    version: Optional[str] = '0.8.2-dev'

    @staticmethod
    def encode(spec: Spec) -> 'SpecRecord':
        return SpecRecord(
            id=spec.id,
            className=spec.className,
            module=spec.module,
            inputs=spec.inputs,
            outputs=spec.outputs,
            init=encrypt(spec.init),
            microservice=spec.microservice,
            node=spec.node,
            form=b64_encoder(spec.form),
            manual=spec.manual,
            author=spec.author,
            license=spec.license,
            version=spec.version
        )

    def decode(self) -> Spec:
        return Spec(
            id=self.id,
            className=self.className,
            module=self.module,
            inputs=self.inputs,
            outputs=self.outputs,
            init=decrypt(self.init),
            microservice=self.microservice,
            node=self.node,
            form=b64_decoder(self.form),
            manual=self.manual,
            author=self.author,
            license=self.license,
            version=self.version
        )


class MetaDataRecord(BaseModel):
    name: str
    brand: Optional[str] = ""
    desc: Optional[str] = ""
    keywords: Optional[List[str]] = []
    type: str = 'flowNode'
    width: int = 300
    height: int = 100
    icon: str = 'plugin'
    documentation: Optional[str] = ""
    group: Optional[List[str]] = ["General"]
    tags: List[str] = []
    pro: bool = False
    commercial: bool = False
    remote: bool = False
    frontend: bool = False
    emits_event: Optional[str] = ""
    purpose: List[str] = ['collection']

    @staticmethod
    def encode(metadata: MetaData) -> 'MetaDataRecord':
        return MetaDataRecord(
            name=metadata.name,
            brand=metadata.brand,
            desc=metadata.desc,
            keywords=metadata.keywords,
            type=metadata.type,
            width=metadata.width,
            height=metadata.height,
            icon=metadata.icon,
            documentation=b64_encoder(metadata.documentation),
            group=metadata.group,
            tags=metadata.tags,
            pro=metadata.pro,
            commercial=metadata.commercial,
            remote=metadata.remote,
            frontend=metadata.frontend,
            emits_event=b64_encoder(metadata.emits_event),
            purpose=metadata.purpose
        )

    def decode(self) -> MetaData:
        return MetaData(
            name=self.name,
            brand=self.brand,
            desc=self.desc,
            keywords=self.keywords,
            type=self.type,
            width=self.width,
            height=self.height,
            icon=self.icon,
            documentation=b64_decoder(self.documentation),
            group=self.group,
            tags=self.tags,
            pro=self.pro,
            commercial=self.commercial,
            remote=self.remote,
            frontend=self.frontend,
            emits_event=b64_decoder(self.emits_event),
            purpose=self.purpose
        )


class PluginRecord(BaseModel):
    start: bool = False
    debug: bool = False
    spec: SpecRecord
    metadata: MetaDataRecord

    @staticmethod
    def encode(plugin: Plugin) -> 'PluginRecord':
        return PluginRecord(
            start=plugin.start,
            debug=plugin.debug,
            spec=SpecRecord.encode(plugin.spec),
            metadata=MetaDataRecord.encode(plugin.metadata)
        )

    def decode(self) -> Plugin:
        data = {
            "start": self.start,
            "debug": self.debug,
            "spec": self.spec.decode(),
            "metadata": self.metadata.decode()
        }
        return Plugin.model_construct(_fields_set=self.model_fields_set, **data)


class FlowRecord(NamedEntity):
    timestamp: Optional[datetime] = None
    deploy_timestamp: Optional[datetime] = None
    description: Optional[str] = None
    projects: Optional[List[str]] = ["General"]
    draft: Optional[str] = ''
    production: Optional[str] = ''
    backup: Optional[str] = ''
    lock: bool = False
    deployed: Optional[bool] = False
    type: str

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'flow',
            FlowRecord
        )

    def get_production_workflow(self) -> 'Flow':
        return Flow.from_workflow_record(self, output='production')

    def get_draft_workflow(self) -> 'Flow':
        return Flow.from_workflow_record(self, output='draft')

    def get_empty_workflow(self, id) -> 'Flow':
        return Flow.build(id=id, name=self.name, description=self.description,
                          projects=self.projects, lock=self.lock)

    def restore_production_from_backup(self):
        if not self.backup:
            raise ValueError("Back up is empty.")
        self.production = self.backup

    def restore_draft_from_production(self):
        if not self.production:
            raise ValueError("Production up is empty.")
        self.draft = self.production

    def set_lock(self, lock: bool = True) -> None:
        self.lock = lock
        production_flow = self.get_production_workflow()
        production_flow.lock = lock
        self.production = encrypt(production_flow.model_dump())
        draft_flow = self.get_draft_workflow()
        draft_flow.lock = lock
        self.draft = encrypt(draft_flow.model_dump())
