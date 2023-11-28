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
class TriggerTable(Base):
    __tablename__ = 'trigger'

    id = Column(String(40))  # 'keyword' in ES with ignore_above
    tenant = Column(String(40))
    production = Column(Boolean)
    name = Column(String(150), index=True)  # 'keyword' in ES with ignore_above
    description = Column(String(255))  # 'text' in ES with no string length mentioned
    type = Column(String(64))  # 'keyword' in ES defaults to 255 if no ignore_above is set
    metadata_time_insert = Column(DateTime)  # Nested 'date' fields
    event_type_id = Column(String(40))  # Nested 'keyword' fields
    event_type_name = Column(String(64))  # Nested 'keyword' fields
    flow_id = Column(String(40), index=True)  # Nested 'keyword' fields
    flow_name = Column(String(64))  # Nested 'text' fields with no string length mentioned
    segment_id = Column(String(40), index=True)  # Nested 'keyword' fields
    segment_name = Column(String(64))  # Nested 'text' fields with no string length mentioned
    source_id = Column(String(40), index=True)  # Nested 'keyword' fields
    source_name = Column(String(64))  # Nested 'text' fields with no string length mentioned
    properties = Column(JSON)  # 'object' in ES is mapped to 'JSON' in MySQL
    enabled = Column(Boolean)  # 'boolean' in ES is mapped to BOOLEAN in MySQL
    tags = Column(String(255), index=True)  # 'keyword' in ES defaults to 255 if no ignore_above is set

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )
```

and it to the corresponding object `Rule` that has the following schema:

```python
from datetime import datetime
from typing import Optional, Any, List, Set

from pydantic import field_validator, PrivateAttr

from .metadata import Metadata
from .named_entity import NamedEntity
from .time import Time
from .value_object.storage_info import StorageInfo


class Rule(NamedEntity):

    _schedule_node_id: str = PrivateAttr(None)
    event_type: Optional[NamedEntity] = NamedEntity(id="", name="")
    type: Optional[str] = 'event-collect'
    flow: NamedEntity
    source: Optional[NamedEntity] = NamedEntity(id="", name="")
    segment: Optional[NamedEntity] = NamedEntity(id="", name="")
    enabled: Optional[bool] = True
    description: Optional[str] = "No description provided"
    properties: Optional[dict] = None
    metadata: Optional[Metadata] = None
    tags: Optional[List[str]] = ["General"]

    @field_validator("tags")
    @classmethod
    def tags_can_not_be_empty(cls, value):
        if len(value) == 0:
            value = ["General"]
        return value

    def set_as_scheduled(self, schedule_node_id):
        self._schedule_node_id = schedule_node_id

    def schedule_node_id(self):
        return self._schedule_node_id

    def are_consents_met(self, profile_consent_ids: Set[str]) -> bool:
        if self.properties is None:
            # No restriction
            return True

        if not profile_consent_ids:
            # No consents set on profile
            return True

        if 'consents' in self.properties and isinstance(self.properties['consents'], list):
            if len(self.properties['consents']) > 0:
                required_consent_ids = set([item['id'] for item in self.properties['consents'] if 'id' in item])
                return required_consent_ids.intersection(profile_consent_ids) == required_consent_ids

        return True

    def __init__(self, **data: Any):
        if 'metadata' not in data:
            data['metadata'] = Metadata(
                time=Time(
                    insert=datetime.utcnow()
                ))
        super().__init__(**data)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'rule',
            Rule
        )

```

create function `map_to_<oject-name>table` that maps domain object to sqlalchemy table. And function `map_to_<object-name>` that
converts table values to domain object. Return only mapping functions, Do not printout the Table or Object definitions. 