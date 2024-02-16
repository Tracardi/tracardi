YOur task is to create a python code that will convert pydantic model to SQlAlchemy table.

For Example:

An object:

```python

class NamedEntityInContext(NamedEntity):
    production: Optional[bool] = False
    running: Optional[bool] = False

class DestinationConfig(BaseModel):
    package: str
    init: dict = {}
    form: dict = {}
    pro:bool = False

class Destination(NamedEntityInContext):
    description: Optional[str] = ""
    destination: DestinationConfig
    enabled: bool = False
    tags: List[str] = []
    mapping: dict = {}
    condition: Optional[str] = ""
    on_profile_change_only: Optional[bool] = True
    resource: Entity
    event_type: Optional[NamedEntity] = None
    source: NamedEntity
```

Should be converted into SQLAlchemy table:

```python
class DestinationTable(Base):
    __tablename__ = 'destination'

    id = Column(String(40))
    name = Column(String(128), index=True)

    description = Column(Text)
    destination = Column(JSON)
    condition = Column(Text)
    mapping = Column(JSON)
    enabled = Column(Boolean, default=False)
    on_profile_change_only = Column(Boolean)
    event_type_id = Column(String(40))
    event_type_name = Column(String(128))
    source_id = Column(String(40))
    source_name = Column(String(128))
    resource_id = Column(String(40), index=True)
    tags = Column(String(255))

    tenant = Column(String(40))
    production = Column(Boolean)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

    running: bool = False
```

Notice that table have all embedded object flattened eg. event_type_id and event_type_name represents data from event_type: Optional[NamedEntity] = None.
Notice also the table has 2 more fields that are not present in pydantic object (tenant, and production). Please do not convert nested object onto join = Column(JSON). Flatten them in the table fields

Please convert the following code into the SQLAlchemy table:

```python
from typing import Optional, List
from pydantic import BaseModel, field_validator

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.ref_value import RefValue


class AudienceAggregate(BaseModel):
    aggr: str
    by_field: RefValue
    save_as: str

class DependentEntity(BaseModel):
    type: str
    event_type: Optional[NamedEntity] = None
    where: Optional[str] = ""

class AudienceGroupBy(BaseModel):
    entity: Optional[DependentEntity] = None
    group_by: Optional[List[AudienceAggregate]] = []
    group_where: Optional[str] = ""

    def is_empty(self) -> bool:
        return self.entity is None or (self.group_where == "" and not self.group_by)

    def __hash__(self):
        return hash(f"{self}")


class Audience(NamedEntity):
    description: Optional[str] = ""
    enabled: bool = False
    tags: List[str] = []
    join: List[AudienceGroupBy] = []

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value):
        if not value:
            raise ValueError("Name can not be empty")
        return value

```