import uuid
from tracardi_graph_runner.domain.flow import Flow as GraphFlow
from .named_entity import NamedEntity
from .value_object.storage_info import StorageInfo
from typing import Optional, List, Any
from pydantic import BaseModel, root_validator
from tracardi_graph_runner.domain.flow_graph_data import FlowGraphData, Edge, Position, Node, EdgeBundle
from tracardi_plugin_sdk.domain.register import MetaData, Plugin, Spec, Form

from ..config import tracardi
from ..service.secrets import decrypt, encrypt
import logging

logger = logging.getLogger("Flow")
logger.setLevel(logging.WARNING)


class FlowSchema(BaseModel):
    version: str = tracardi.version
    uri: str = 'http://www.tracardi.com/2021/WFSchema'
    server_version: str = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.server_version = tracardi.version


class Flow(GraphFlow):
    projects: Optional[List[str]] = ["General"]
    lock: bool = False
    wf_schema: FlowSchema

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
            wf_schema=FlowSchema(version=tracardi.version),
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
            wf_schema=FlowSchema(version=tracardi.version),
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
    form: Optional[Form]
    manual: Optional[str] = None
    author: Optional[str] = None
    license: Optional[str] = "MIT"
    version: Optional[str] = '0.0.1'

    @staticmethod
    def encode(spec: Spec) -> 'SpecRecord':
        return SpecRecord(
            id=spec.id,
            className=spec.className,
            module=spec.module,
            inputs=spec.inputs,
            outputs=spec.outputs,
            init=encrypt(spec.init),
            form=spec.form,
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
            form=self.form,
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
        self.production = self.backup

    def restore_draft_from_production(self):
        self.draft = self.production
