import uuid
from tracardi.service.wf.domain.flow import Flow as GraphFlow
from .named_entity import NamedEntity
from .value_object.storage_info import StorageInfo
from typing import Optional, List, Any
from pydantic import BaseModel
from tracardi.service.wf.domain.flow_graph_data import FlowGraphData, Edge, Position, Node, EdgeBundle
from tracardi.service.plugin.domain.register import MetaData, Plugin, Spec, NodeEvents

from ..config import tracardi
from ..service.secrets import decrypt, encrypt, b64_encoder, b64_decoder
import logging

logger = logging.getLogger("Flow")
logger.setLevel(tracardi.logging_level)


class FlowSchema(BaseModel):
    version: str = tracardi.version.version
    uri: str = 'http://www.tracardi.com/2021/WFSchema'
    server_version: str = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.server_version = tracardi.version.version


class Flow(GraphFlow):
    projects: Optional[List[str]] = ["General"]
    lock: bool = False
    wf_schema: FlowSchema = FlowSchema()

    def get_production_workflow_record(self) -> 'FlowRecord':

        production = encrypt(self.dict())

        return FlowRecord(
            id=self.id,
            description=self.description,
            name=self.name,
            enabled=self.enabled,
            projects=self.projects,
            draft=production,
            production=production,
            lock=self.lock
        )

    def get_empty_workflow_record(self) -> 'FlowRecord':

        return FlowRecord(
            id=self.id,
            description=self.description,
            name=self.name,
            enabled=self.enabled,
            projects=self.projects,
            lock=self.lock
        )

    @staticmethod
    def new(id: str = None) -> 'Flow':
        return Flow(
            id=str(uuid.uuid4()) if id is None else id,
            name="Empty",
            wf_schema=FlowSchema(version=str(tracardi.version)),
            enabled=False,
            flowGraph=FlowGraphData(nodes=[], edges=[])
        )

    @staticmethod
    def build(name: str, description: str = None, enabled=True, id=None, lock=False, projects=None) -> 'Flow':
        if projects is None:
            projects = ["General"]

        return Flow(
            id=str(uuid.uuid4()) if id is None else id,
            name=name,
            wf_schema=FlowSchema(version=str(tracardi.version)),
            description=description,
            enabled=enabled,
            projects=projects,
            lock=lock,
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
    id: str
    className: str
    module: str
    inputs: Optional[List[str]] = []
    outputs: Optional[List[str]] = []
    init: Optional[str] = ""
    node: Optional[NodeEvents] = None
    form: Optional[str] = ""
    manual: Optional[str] = None
    author: Optional[str] = None
    license: Optional[str] = "MIT"
    version: Optional[str] = '0.6.2'

    @staticmethod
    def encode(spec: Spec) -> 'SpecRecord':
        return SpecRecord(
            id=spec.id,
            className=spec.className,
            module=spec.module,
            inputs=spec.inputs,
            outputs=spec.outputs,
            init=encrypt(spec.init),
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
    frontend: bool = False
    emits_event: Optional[str] = ""

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
            frontend=metadata.frontend,
            emits_event=b64_encoder(metadata.emits_event)
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
            frontend=self.frontend,
            emits_event=b64_decoder(self.emits_event)
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
        return Plugin.construct(_fields_set=self.__fields_set__, **data)


class FlowRecord(NamedEntity):
    description: Optional[str] = None
    enabled: Optional[bool] = True
    projects: Optional[List[str]] = ["General"]
    draft: Optional[str] = ''
    production: Optional[str] = ''
    backup: Optional[str] = ''
    lock: bool = False

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'flow',
            FlowRecord
        )

    def get_production_workflow(self) -> 'Flow':
        decrypted = decrypt(self.production)
        return Flow(**decrypted)

    def get_draft_workflow(self) -> 'Flow':
        decrypted = decrypt(self.draft)
        return Flow(**decrypted)

    def get_empty_workflow(self, id) -> 'Flow':
        return Flow.build(id=id, name=self.name, description=self.description, enabled=self.enabled,
                          projects=self.projects, lock=self.lock)

    def restore_production_from_backup(self):
        if not self.backup:
            raise ValueError("Back up is empty.")
        self.production = self.backup

    def restore_draft_from_production(self):
        if not self.production:
            raise ValueError("Production up is empty.")
        self.draft = self.production
