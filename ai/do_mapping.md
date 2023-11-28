You a python programmer. Here a a simple code that based on the SqlAlchemy Tabel and some Domain object creates a
mapping functions `map_to_<object-name>_table` thats maps domain object to sqlalchemy table. And function `map_to_<object-name>` that
converts table value to domain object.

Here is a simple mapping functions for Bridge table:

```python
class BridgeTable(Base):
    __tablename__ = 'bridge'

    id = Column(String(40))  # 'keyword' with ignore_above maps to VARCHAR with length
    tenant = Column(String(32))
    production = Column(Boolean)
    name = Column(String(64))  # 'text' type in ES maps to VARCHAR(255) in MySQL
    description = Column(Text)  # 'text' type in ES maps to VARCHAR(255) in MySQL
    type = Column(String(48))  # 'keyword' type in ES maps to VARCHAR(255) in MySQL
    config = Column(JSON)  # 'object' type in ES with 'enabled' false maps to JSON in MySQL
    form = Column(JSON)  # 'object' type in ES with 'enabled' false maps to JSON in MySQL
    manual = Column(Text, nullable=True)  # 'keyword' type in ES with 'index' false maps to VARCHAR(255) in MySQL
    nested_value = Column(String(48))  # this is nestedvalue for object nested
    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )
```

And here is the mapping

```python
from tracardi.context import get_context
from tracardi.domain.bridge import Bridge
from tracardi.service.plugin.domain.register import Form
from tracardi.service.storage.mysql.schema.table import BridgeTable
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json


def map_to_bridge_table(bridge: Bridge) -> BridgeTable:
    context = get_context()
    return BridgeTable(
        id=bridge.id,
        tenant=context.tenant,
        production=context.production,
        name=bridge.name,
        description=bridge.description or "", # Ads default value if bridge.description not available
        type=bridge.type,
        config=to_json(bridge.config),
        form=to_json(bridge.form),
        manual=bridge.manual,
        nested_value = bridge.nested.value if bridge.nested else True # Ads default value if bridge.nested not available
    )


def map_to_bridge(bridge_table: BridgeTable) -> Bridge:
    return Bridge(
        id=bridge_table.id,
        name=bridge_table.name,
        description=bridge_table.description or "",  # Ads default value if bridge_table.description not available
        type=bridge_table.type,
        config=from_json(bridge_table.config),
        form=from_json(bridge_table.form, Form),
        manual=bridge_table.manual,
        nested=Nested(value=bridge_table.nested_value) if bridge_table.nested_value else None  # Ads default value
        
    )
```

The domain Bridge object looks like this:

```python
from typing import Optional
from pydantic import BaseModel

from tracardi.domain.named_entity import NamedEntity


class FormFieldValidation(BaseModel):
    regex: str
    message: str


class FormComponent(BaseModel):
    type: str = 'text'
    props: Optional[dict] = {}


class FormField(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    component: FormComponent
    validation: Optional[FormFieldValidation] = None
    required: bool = False


class FormGroup(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: List[FormField]


class Form(BaseModel):
    submit: Optional[str] = None
    default: Optional[dict] = {}
    title: Optional[str] = None
    groups: Optional[List[FormGroup]] = []


class Nested(BaseModel):
    value: Optional[bool] = True
    
    
class Bridge(NamedEntity):
    description: Optional[str] = ""  # The Default value should be added to mapping if description not available
    type: str
    config: Optional[dict] = {}
    form: Optional[Form] = None
    manual: Optional[str] = None
    nested: Optional[Nested]=None
```
----

# Your task 

Based on the sqlalchemy table:

```python
class WorkflowTable(Base):
    __tablename__ = 'workflow'

    id = Column(String(40))
    timestamp = Column(DateTime)
    deploy_timestamp = Column(DateTime)
    name = Column(String(64), index=True)
    description = Column(String(255))
    type = Column(String(64), default="collection", index=True)
    projects = Column(String(255))

    draft = Column(LargeBinary)
    prod = Column(LargeBinary)
    backup = Column(LargeBinary)

    lock = Column(Boolean)
    deployed = Column(Boolean, default=False)
    debug_enabled = Column(Boolean)
    debug_logging_level = Column(String(32))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )
```

and it to the corresponding object `FlowRecord` that has the following schema:

```python
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
            timestamp=datetime.utcnow(),
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
            flow.timestamp = datetime.utcnow()

        return flow

    @staticmethod
    def new(id: str = None) -> 'Flow':
        return Flow(
            id=str(uuid.uuid4()) if id is None else id,
            timestamp=datetime.utcnow(),
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
            timestamp=datetime.utcnow(),
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

```

create function `map_to_<oject-name>table` that maps domain object to sqlalchemy table. And function `map_to_<object-name>` that
converts table values to domain object. Return only mapping functions, Do not printout the Table or Object definitions. 