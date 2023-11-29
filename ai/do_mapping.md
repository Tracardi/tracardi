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
class ReportTable(Base):
    __tablename__ = 'report'

    id = Column(String(40))  # 'keyword' type in ES corresponds to 'VARCHAR' in MySQL with ignore_above
    name = Column(String(128))  # Elasticsearch 'text' type is similar to MySQL 'VARCHAR'
    description = Column(Text)  # 'text' type in ES corresponds to 'VARCHAR' in MySQL
    tags = Column(String(128))  # 'keyword' type in ES corresponds to 'VARCHAR' in MySQL
    index = Column(String(128))  # 'text' type in ES corresponds to 'VARCHAR' in MySQL
    query = Column(JSON)  # 'text' type in ES corresponds to 'VARCHAR' in MySQL, 'index' property in ES ignored
    enabled = Column(Boolean, default=True)  # 'boolean' type in ES is the same as in MySQL, default value set from 'null_value'
    

    tenant = Column(String(40))  # Field added for multitenance
    production = Column(Boolean) # Field added for multitenance

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )
```

and it to the corresponding object `Report` that has the following schema:

```python
from tracardi.domain.named_entity import NamedEntity
from pydantic import field_validator
from typing import List
from tracardi.service.secrets import encrypt, decrypt
import json
import re


class QueryBuildingError(Exception):
    pass


class ReportRecord(NamedEntity):
    description: str
    index: str
    query: str
    tags: List[str]


class Report(NamedEntity):
    _regex = re.compile(r"\"\{{2}\s*([0-9a-zA-Z_]+)\s*\}{2}\"")
    description: str
    index: str
    query: dict
    tags: List[str]

    @field_validator("index")
    @classmethod
    def validate_entity(cls, value):
        if value not in ("profile", "session", "event", "entity"):
            raise ValueError(f"Entity has to be one of: profile, session, event, entity. `{value}` given.")
        return value

    def encode(self) -> ReportRecord:
        return ReportRecord(
            id=self.id,
            name=self.name,
            description=self.description,
            tags=self.tags,
            index=self.index,
            query=encrypt(self.query)
        )

    @staticmethod
    def decode(record: ReportRecord) -> 'Report':
        return Report(
            id=record.id,
            name=record.name,
            description=record.description,
            index=record.index,
            tags=record.tags,
            query=decrypt(record.query)
        )

    @staticmethod
    def _format_value(value) -> str:
        return f"\"{value}\"" if isinstance(value, str) else str(value)

    def get_built_query(self, **kwargs) -> dict:
        try:
            query = json.dumps(self.query)
            query = re.sub(
                self._regex,
                lambda x: self._format_value(kwargs[x.group(1)]),
                query
            )
            return json.loads(query)
        except KeyError as e:
            raise QueryBuildingError(f"Missing parameter: {str(e)}")

        except Exception as e:
            raise QueryBuildingError(str(e))

    @property
    def expected_query_params(self) -> List[str]:
        return re.findall(self._regex, json.dumps(self.query))

    def __eq__(self, other: 'Report') -> bool:
        return self.id == other.id \
               and json.dumps(self.query) == json.dumps(other.query) \
               and self.name == other.name \
               and self.index == other.index \
               and self.description == other.description \
               and self.tags == other.tags



```

create function `map_to_<oject-name>table` that maps domain object to sqlalchemy table. And function `map_to_<object-name>` that
converts table values to domain object. Return only mapping functions, Do not printout the Table or Object definitions. 