from datetime import datetime
from typing import Optional, List, Union, Any
from uuid import uuid4

from .entity import Entity
from .event_metadata import EventMetadata
from pydantic import BaseModel, root_validator
from typing import Tuple

from .marketing import UTM
from .metadata import OS, Device, Application, Hit
from .named_entity import NamedEntity
from .profile import ProfileLoyalty, ProfileJob, ProfilePreference, ProfileMedia, \
    ProfileIdentifier, ProfileContact, ProfilePII
from .value_object.operation import RecordFlag
from .value_object.storage_info import StorageInfo
from ..service.string_manager import capitalize_event_type_id


class Tags(BaseModel):
    values: Tuple['str', ...] = ()
    count: int = 0

    class Config:
        validate_assignment = True

    @root_validator
    def total_tags(cls, values):
        values["count"] = len(values.get("values"))
        return values

    def add(self, tag: Union[str, List[str]]):

        if isinstance(tag, list):
            tag = tuple(tag)
            self.values += tag
        else:
            self.values += tag,

        self.count = len(self.values)


class EventSession(Entity):
    start: datetime = datetime.utcnow()
    duration: float = 0
    tz: Optional[str] = 'utc'


class EventJourney(BaseModel):
    state: Optional[str] = None


class EventProductVariant(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None


class EventCheckout(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    value: Optional[float] = 0


class EventIncome(BaseModel):
    value: Optional[float] = 0
    revenue: Optional[float] = 0


class EventCost(BaseModel):
    shipping: Optional[float] = 0
    tax: Optional[float] = 0
    discount: Optional[float] = 0
    other: Optional[float] = 0


class EventProduct(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    variant: Optional[str] = None
    price: Optional[float] = 0
    quantity: Optional[int] = 0
    position: Optional[int] = 0
    review: Optional[str] = None
    rate: Optional[float] = 0


class EventOrder(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    income: Optional[EventIncome] = EventIncome()
    cost: Optional[EventCost] = EventCost()
    affiliation: Optional[str] = None


class EventEc(BaseModel):
    product: Optional[EventProduct] = EventProduct()
    checkout: Optional[EventCheckout] = EventCheckout()
    order: Optional[EventOrder] = EventOrder()


class EventMessage(BaseModel):
    type: Optional[str] = None
    text: Optional[str] = None
    recipient: Optional[str] = None


class EventCreditCard(BaseModel):
    number: Optional[str] = None
    expires: Optional[datetime] = None
    holder: Optional[str] = None


class EventPayment(BaseModel):
    method: Optional[str] = None
    credit_card: Optional[EventCreditCard] = EventCreditCard()


class EventPromotion(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


class EventMarketing(BaseModel):
    coupon: Optional[str] = None
    promotion: Optional[EventPromotion] = EventPromotion()


class EventData(BaseModel):
    pii: Optional[ProfilePII] = ProfilePII()
    contact: Optional[ProfileContact] = ProfileContact()
    identifier: Optional[ProfileIdentifier] = ProfileIdentifier()
    media: Optional[ProfileMedia] = ProfileMedia()
    preferences: Optional[ProfilePreference] = ProfilePreference()
    job: Optional[ProfileJob] = ProfileJob()
    loyalty: Optional[ProfileLoyalty] = ProfileLoyalty()
    ec: Optional[EventEc] = EventEc()
    message: Optional[EventMessage] = EventMessage()
    payment: Optional[EventPayment] = EventPayment()
    marketing: Optional[EventMarketing] = EventMarketing()


class Event(NamedEntity):
    metadata: EventMetadata
    type: str

    device: Optional[Device] = Device()
    os: Optional[OS] = OS()
    app: Optional[Application] = Application()
    hit: Optional[Hit] = Hit()

    utm: Optional[UTM] = UTM()

    properties: Optional[dict] = {}
    traits: Optional[dict] = {}
    operation: RecordFlag = RecordFlag()

    source: Entity
    session: Optional[EventSession] = None
    profile: Optional[Entity] = None
    context: Optional[dict] = {}
    request: Optional[dict] = {}
    config: Optional[dict] = {}
    tags: Tags = Tags()
    journey: EventJourney = EventJourney()
    aux: dict = {}

    data: Optional[EventData] = EventData()

    def __init__(self, **data: Any):
        if 'type' in data and isinstance(data['type'], str):
            data['type'] = data['type'].lower().replace(' ', '-')
        if 'name' not in data:
            data['name'] = capitalize_event_type_id(data['type'])
        super().__init__(**data)

    def replace(self, event):
        if isinstance(event, Event):
            self.id = event.id
            self.metadata = event.metadata
            self.type = event.type
            self.properties = event.properties
            self.traits = event.traits
            # do not replace those - read only
            # self.source = event.source
            # self.session = event.session
            # self.profile = event.profile
            self.context = event.context
            self.request = event.request
            self.config = event.config
            self.tags = event.tags
            self.aux = event.aux
            self.os = event.os
            self.device = event.device
            self.app = event.app

    def get_ip(self):
        if 'headers' in self.request and 'x-forwarded-for' in self.request['headers']:
            return self.request['headers']['x-forwarded-for']
        return None

    def is_persistent(self) -> bool:
        if 'save' in self.config and isinstance(self.config['save'], bool):
            return self.config['save']
        else:
            return True

    def has_profile(self) -> bool:
        return self.profile is not None

    def has_session(self) -> bool:
        return self.session is not None

    @staticmethod
    def new(data: dict) -> 'Event':
        data['id'] = str(uuid4())
        return Event(**data)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'event',
            Event,
            multi=True
        )
