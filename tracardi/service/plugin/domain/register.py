import hashlib
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, AnyHttpUrl

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resources.microservice_resource import MicroserviceResource


class FormFieldValidation(BaseModel):
    regex: str
    message: str


class FormComponent(BaseModel):
    type: str = 'text'
    props: Optional[dict] = {}


class FormField(BaseModel):
    id: str
    name: str
    description: Optional[str]
    component: FormComponent
    validation: Optional[FormFieldValidation]
    required: bool = False


class FormGroup(BaseModel):
    name: Optional[str]
    description: Optional[str]
    fields: List[FormField]


class Form(BaseModel):
    title: Optional[str]
    groups: List[FormGroup]


class RunOnce(BaseModel):
    value: Optional[str] = ""
    ttl: int = 0
    type: str = "value"
    enabled: bool = False


class NodeEvents(BaseModel):
    on_remove: Optional[str]
    on_create: Optional[str]


class MicroserviceCurrentResource(NamedEntity):
    current: MicroserviceResource


class MicroserviceConfig(BaseModel):
    resource: MicroserviceCurrentResource
    plugin: NamedEntity

    def has_resource(self) -> bool:
        return bool(self.resource.id)


class Spec(BaseModel):
    id: Optional[str]
    className: str
    module: str
    inputs: Optional[List[str]] = []
    outputs: Optional[List[str]] = []
    init: Optional[dict] = None
    microservice: Optional[MicroserviceConfig] = None
    skip: bool = False
    block_flow: bool = False
    run_in_background: bool = False
    on_error_continue: bool = False
    on_connection_error_repeat: int = 1
    append_input_payload: bool = False
    join_input_payload: bool = False
    form: Optional[Form]
    manual: Optional[str] = None
    author: Optional[str] = None
    license: Optional[str] = "MIT"
    version: Optional[str] = '0.7.2-dev'
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
        # You can create one microservice per remote resource.
        if self.has_microservice() and self.microservice.has_resource():
            action_id += self.microservice.resource.id

        return hashlib.md5(action_id.encode()).hexdigest()


class PortDoc(BaseModel):
    desc: str


class Documentation(BaseModel):
    tutorial: Optional[str]
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
    remote: bool = False
    frontend: bool = False
    emits_event: Optional[Dict[str, str]] = {}


class Plugin(BaseModel):
    start: bool = False
    debug: bool = False
    spec: Spec
    metadata: MetaData
