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
class EventSourceTable(Base):
    __tablename__ = 'event_source'

    id = Column(String(40))
    tenant = Column(String(40))
    production = Column(Boolean)
    timestamp = Column(DateTime)
    update = Column(DateTime)
    type = Column(String(32))
    bridge_id = Column(String(40))
    bridge_name = Column(String(128), ForeignKey('bridge.id'))
    name = Column(String(64))
    description = Column(String(255))
    channel = Column(String(32))
    url = Column(String(255))
    enabled = Column(Boolean)
    locked = Column(Boolean)
    transitional = Column(Boolean)
    tags = Column(String(255))
    groups = Column(String(255))
    icon = Column(String(32))
    config = Column(JSON)
    configurable = Column(Boolean)
    hash = Column(String(255))
    returns_profile = Column(Boolean)
    permanent_profile_id = Column(Boolean)
    requires_consent = Column(Boolean)
    synchronize_profiles = Column(Boolean)
    manual = Column(String(64))
    endpoints_get_url = Column(String(255))
    endpoints_get_method = Column(String(255))
    endpoints_post_url = Column(String(255))
    endpoints_post_method = Column(String(255))

    bridge = relationship("BridgeTable")

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )
```

and it to the object EventSource that has the following schema:

```python
from datetime import datetime
from typing import Optional, Union, List, Any

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.domain.entity import Entity


class EventSource(Entity):
    type: List[str]
    bridge: NamedEntity
    timestamp: datetime
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    channel: Optional[str] = ""
    enabled: Optional[bool] = True
    transitional: Optional[bool] = False
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    returns_profile: Optional[bool] = False   # Todo remove - not used
    permanent_profile_id: Optional[bool] = False
    requires_consent: Optional[bool] = False
    manual: Optional[str] = None
    locked: bool = False
    synchronize_profiles: bool = True
    config: Optional[dict] = None

```

create function `map_to_<oject-name>table` that maps domain object to sqlalchemy table. And function `map_to_<object-name>` that
converts table values to domain object.