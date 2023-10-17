import hashlib
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resource import ResourceCredentials


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


class RunOnce(BaseModel):
    value: Optional[str] = ""
    ttl: int = 0
    type: str = "value"
    enabled: bool = False


class NodeEvents(BaseModel):
    on_remove: Optional[str] = None
    on_create: Optional[str] = None


class MicroservicePlugin(NamedEntity):
    resource: Optional[dict] = {}  # Additional resources needed for microservice plugin


class MicroserviceServer(BaseModel):
    credentials: ResourceCredentials
    resource: NamedEntity  # Selected tracardi resource


class MicroserviceConfig(BaseModel):
    server: MicroserviceServer  # Server configuration from premium resources
    service: NamedEntity
    plugin: MicroservicePlugin

    def has_server_resource(self) -> bool:
        return bool(self.server.resource.id)

    @staticmethod
    def create() -> 'MicroserviceConfig':
        return MicroserviceConfig(
            server=MicroserviceServer(
                credentials=ResourceCredentials(),
                resource=NamedEntity(
                    id="",
                    name=""
                )
            ),
            service=NamedEntity(
                id="",
                name=""
            ),
            plugin=MicroservicePlugin(
                id="",
                name=""
            )
        )


class Spec(BaseModel):
    id: Optional[str] = None
    className: str
    module: str
    inputs: Optional[List[str]] = []
    outputs: Optional[List[str]] = []
    init: Optional[dict] = None
    microservice: Optional[MicroserviceConfig] = MicroserviceConfig.create()
    skip: bool = False
    block_flow: bool = False
    run_in_background: bool = False
    on_error_continue: bool = False
    on_connection_error_repeat: int = 1
    append_input_payload: bool = False
    join_input_payload: bool = False
    form: Optional[Form] = None
    manual: Optional[str] = None
    author: Optional[str] = None
    license: Optional[str] = "MIT"
    version: Optional[str] = '0.8.2'
    run_once: Optional[RunOnce] = RunOnce()
    node: Optional[NodeEvents] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.id = self.get_id()

    def has_microservice(self):
        return self.microservice is not None

    def get_id(self) -> str:
        action_id = self.module + self.className + self.version
        # If defined resource for microservice plugin action add that to the id.
        # You can create one microservice per remote server.
        if self.has_microservice() and self.microservice.has_server_resource():
            action_id += self.microservice.server.resource.id

        return hashlib.md5(action_id.encode()).hexdigest()


class PortDoc(BaseModel):
    desc: str


class Documentation(BaseModel):
    tutorial: Optional[str] = None
    inputs: Dict[str, PortDoc]
    outputs: Dict[str, PortDoc]


class MetaData(BaseModel):
    name: str
    brand: Optional[str] = "Tracardi"
    desc: Optional[str] = ""
    keywords: Optional[List[str]] = []
    type: str = 'flowNode'
    width: int = 300
    height: int = 100
    icon: str = 'plugin'
    documentation: Optional[Documentation] = None
    group: Optional[List[str]] = ["General"]
    tags: List[str] = []
    pro: bool = False
    commercial: bool = False
    remote: bool = False
    frontend: bool = False
    emits_event: Optional[Dict[str, str]] = {}
    purpose: List[str] = ['collection']


class Plugin(BaseModel):
    start: bool = False
    debug: bool = False
    spec: Spec
    metadata: MetaData
