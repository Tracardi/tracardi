from datetime import datetime
from typing import Optional, List, Union, Any
from uuid import uuid4

from .entity import Entity
from .event_metadata import EventMetadata
from pydantic import model_validator, ConfigDict, BaseModel
from typing import Tuple

from .marketing import UTM
from .named_entity import NamedEntity
from .profile_data import ProfileLoyalty, ProfileJob, ProfilePreference, ProfileMedia, \
    ProfileIdentifier, ProfileContact, ProfilePII
from .value_object.operation import RecordFlag
from .value_object.storage_info import StorageInfo
from ..service.string_manager import capitalize_event_type_id
from ..service.utils.date import now_in_utc


class Tags(BaseModel):
    values: Tuple['str', ...] = ()
    count: int = 0
    model_config = ConfigDict(validate_assignment=True)

    @model_validator(mode="before")
    @classmethod
    def total_tags(cls, values):
        values["count"] = len(values.get("values", []))
        return values

    def add(self, tag: Union[str, List[str]]):

        if isinstance(tag, list):
            tag = tuple(tag)
            self.values += tag
        else:
            self.values += tag,

        self.count = len(self.values)


class EventSession(Entity):
    start: datetime = now_in_utc()
    duration: float = 0
    tz: Optional[str] = None


class EventJourney(BaseModel):
    state: Optional[str] = None

    def is_empty(self) -> bool:
        return self.state is None or self.state == ""


class EventProductVariant(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None


class EventCheckout(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    value: Optional[float] = 0


class Money(BaseModel):
    value: Optional[float] = 0
    due_date: Optional[datetime] = None
    currency: Optional[str] = None


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
    receivable: Optional[Money] = Money()
    payable: Optional[Money] = Money()
    income: Optional[Money] = Money()
    cost: Optional[Money] = Money()
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
    pii: Optional[ProfilePII] = ProfilePII.model_construct()
    contact: Optional[ProfileContact] = ProfileContact.model_construct()
    identifier: Optional[ProfileIdentifier] = ProfileIdentifier.model_construct()
    media: Optional[ProfileMedia] = ProfileMedia.model_construct()
    preferences: Optional[ProfilePreference] = ProfilePreference.model_construct()
    job: Optional[ProfileJob] = ProfileJob.model_construct()
    loyalty: Optional[ProfileLoyalty] = ProfileLoyalty.model_construct()
    ec: Optional[EventEc] = EventEc.model_construct()
    message: Optional[EventMessage] = EventMessage.model_construct()
    payment: Optional[EventPayment] = EventPayment.model_construct()
    marketing: Optional[EventMarketing] = EventMarketing.model_construct()


class Event(NamedEntity):
    metadata: EventMetadata
    type: str

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
    aux: dict = {}

    device: Optional[dict] = {}
    os: Optional[dict] = {}
    app: Optional[dict] = {}
    hit: Optional[dict] = {}
    # journey: Optional[dict] = {}
    data: Optional[dict] = {}

    # device: Optional[Device] = Device.construct()
    # os: Optional[OS] = OS.construct()
    # app: Optional[Application] = Application.construct()
    # hit: Optional[Hit] = Hit.construct()
    journey: EventJourney = EventJourney.model_construct()
    # data: Optional[EventData] = EventData.construct()

    def __init__(self, **data: Any):
        if 'type' in data and isinstance(data['type'], str):
            data['type'] = data.get('type', '@missing-event-type').lower().replace(' ', '-')
        if 'name' not in data:
            data['name'] = capitalize_event_type_id(data.get('type', ''))
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
            self.utm = event.utm
            self.aux = event.aux
            self.device = event.device
            self.os = event.os
            self.app = event.app
            self.hit = event.hit
            self.data = event.data
            self.journey = event.journey

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

    @staticmethod
    def dictionary(id: str = None,
                   type: str = None,
                   session_id: str = None,
                   profile_id=None,
                   properties: dict = None,
                   context=None) -> dict:
        if context is None:
            context = {}
        if properties is None:
            properties = {}
        return {
            "id": id,
            "type": type,
            "name": capitalize_event_type_id(type),
            "metadata": {
                "aux": {},
                "time": {
                    "insert": None,
                    "create": None,
                    "update": None,
                    "process_time": 0
                },
                "ip": None,
                "status": None,
                "channel": None,
                "processed_by": {
                    "rules": [],
                    "flows": [],
                    "third_party": []
                },
                "profile_less": False,
                "debug": False,
                "valid": True,
                "error": False,
                "warning": False,
                "instance": {
                    "id": None
                }
            },
            "utm": {
                "source": None,
                "medium": None,
                "campaign": None,
                "term": None,
                "content": None
            },
            "properties": properties,
            "traits": {},
            "operation": {
                "new": False,
                "update": False
            },
            "source": {
                "id": None,
                "type": [],
                "bridge": {
                    "id": None,
                    "name": None
                },
                "timestamp": None,
                "name": None,
                "description": None,
                "channel": None,
                "enabled": True,
                "transitional": False,
                "tags": [],
                "groups": [],
                "returns_profile": False,
                "permanent_profile_id": False,
                "requires_consent": False,
                "manual": None,
                "locked": False,
                "synchronize_profiles": True,
                "config": None
            },
            "session": {
                "id": session_id,
                "start": None,
                "duration": 0,
                "tz": "utc"
            },
            "profile": {
                "id": profile_id
            },
            "context": context,
            "request": {},
            "config": {},
            "tags": {
                "values": (),
                "count": 0
            },
            "aux": {},
            "data": {},
            "device": {
                "name": None,
                "brand": None,
                "model": None,
                "type": None,
                "touch": False,
                "ip": None,
                "resolution": None,
                "geo": {
                    "country": {
                        "name": None,
                        "code": None
                    },
                    "city": None,
                    "county": None,
                    "postal": None,
                    "latitude": None,
                    "longitude": None
                },
                "color_depth": None,
                "orientation": None
            },
            "os": {
                "name": None,
                "version": None
            },
            "app": {
                "type": None,
                "name": None,
                "version": None,
                "language": None,
                "bot": False,
                "resolution": None
            },
            "hit": {
                "name": None,
                "url": None,
                "referer": None,
                "query": None,
                "category": None
            },
            "journey": {
                "state": None
            }
        }
