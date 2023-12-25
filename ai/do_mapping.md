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
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, PrimaryKeyConstraint, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DOUBLE

Base = declarative_base()

class EventTable(Base):
    __tablename__ = 'event'

    # Define fields according to Elasticsearch mapping
    id = Column(String(64), primary_key=True)
    name = Column(String(255))

    metadata_aux = Column(JSON)

    metadata_time_insert = Column(DateTime)
    metadata_time_create = Column(DateTime)
    metadata_time_process_time = Column(Float)
    metadata_time_total_time = Column(Float)
    metadata_status = Column(String(32), default="NULL")
    metadata_channel = Column(String(255))
    metadata_ip = Column(String(255))
    metadata_processed_by_rules = Column(String(255))
    metadata_processed_by_flows = Column(String(255))
    metadata_processed_by_third_party = Column(String(255))
    metadata_profile_less = Column(Boolean)
    metadata_valid = Column(Boolean)
    metadata_warning = Column(Boolean)
    metadata_error = Column(Boolean)
    metadata_merge = Column(Boolean)
    metadata_instance_id = Column(String(40))
    metadata_debug = Column(Boolean)

    type = Column(String(255), default="NULL")
    request = Column(JSON)

    source_id = Column(String(64))
    device_name = Column(String(255))
    device_brand = Column(String(255))
    device_model = Column(String(255))
    device_ip = Column(String(18))
    device_type = Column(String(255))
    device_touch = Column(Boolean)
    device_resolution = Column(String(32))
    device_color_depth = Column(Integer)
    device_orientation = Column(String(32))

    device_geo_country_name = Column(String(255))
    device_geo_country_code = Column(String(10))
    device_geo_county = Column(String(64))
    device_geo_city = Column(String(64))
    device_geo_latitude = Column(Float)
    device_geo_longitude = Column(Float)
    device_geo_location = Column(JSON)
    device_geo_postal = Column(String(24))

    os_name = Column(String(64))
    os_version = Column(String(32))

    app_type = Column(String(255))
    app_bot = Column(Boolean)
    app_name = Column(String(255))
    app_version = Column(String(255))
    app_language = Column(String(32))
    app_resolution = Column(String(32))

    hit_name = Column(String(255))
    hit_url = Column(String(255))
    hit_referer = Column(String(255))
    hit_query = Column(String(255))
    hit_category = Column(String(64))
    hit_id = Column(String(32))

    utm_source = Column(String(64))
    utm_medium = Column(String(64))
    utm_campaign = Column(String(64))
    utm_term = Column(String(64))
    utm_content = Column(String(96))

    session_id = Column(String(64))
    session_start = Column(DateTime)
    session_duration = Column(Float)
    session_tz = Column(String(64))

    profile_id = Column(String(64))

    entity_id = Column(String(64))

    aux = Column(JSON)
    trash = Column(JSON)
    config = Column(JSON)
    context = Column(JSON)
    properties = Column(JSON)
    traits = Column(JSON)

    data_media_image = Column(String(255))
    data_media_webpage = Column(String(255))
    data_media_social_twitter = Column(String(255))
    data_media_social_facebook = Column(String(255))
    data_media_social_youtube = Column(String(255))
    data_media_social_instagram = Column(String(255))
    data_media_social_tiktok = Column(String(255))
    data_media_social_linkedin = Column(String(255))
    data_media_social_reddit = Column(String(255))
    data_media_social_other = Column(JSON)

    data_pii_firstname = Column(String(255))
    data_pii_lastname = Column(String(255))
    data_pii_display_name = Column(String(255))
    data_pii_birthday = Column(DateTime)
    data_pii_language_native = Column(String(255))
    data_pii_language_spoken = Column(String(255))
    data_pii_gender = Column(String(255))
    data_pii_education_level = Column(String(255))
    data_pii_civil_status = Column(String(255))
    data_pii_attributes_height = Column(Float)
    data_pii_attributes_weight = Column(Float)
    data_pii_attributes_shoe_number = Column(Float)

    data_identifier_id = Column(String(64))
    data_identifier_badge = Column(String(64))
    data_identifier_passport = Column(String(32))
    data_identifier_credit_card = Column(String(24))
    data_identifier_token = Column(String(96))
    data_identifier_coupons = Column(String(32))

    data_contact_email_main = Column(String(64))
    data_contact_email_private = Column(String(64))
    data_contact_email_business = Column(String(64))
    data_contact_phone_main = Column(String(32))
    data_contact_phone_business = Column(String(32))
    data_contact_phone_mobile = Column(String(32))
    data_contact_phone_whatsapp = Column(String(32))
    data_contact_app_whatsapp = Column(String(255))
    data_contact_app_discord = Column(String(255))
    data_contact_app_slack = Column(String(255))
    data_contact_app_twitter = Column(String(255))
    data_contact_app_telegram = Column(String(255))
    data_contact_app_wechat = Column(String(255))
    data_contact_app_viber = Column(String(255))
    data_contact_app_signal = Column(String(255))
    data_contact_app_other = Column(JSON)
    data_contact_address_town = Column(String(255))
    data_contact_address_county = Column(String(255))
    data_contact_address_country = Column(String(255))
    data_contact_address_postcode = Column(String(255))
    data_contact_address_street = Column(String(255))
    data_contact_address_other = Column(String(255))
    data_contact_confirmations = Column(String(255))

    data_job_position = Column(String(255))
    data_job_salary = Column(Float)
    data_job_type = Column(String(255))
    data_job_company_name = Column(String(255))
    data_job_company_size = Column(String(255))
    data_job_company_segment = Column(String(255))
    data_job_company_country = Column(String(255))
    data_job_department = Column(String(255))

    data_preferences_purchases = Column(String(255))
    data_preferences_colors = Column(String(255))
    data_preferences_sizes = Column(String(255))
    data_preferences_devices = Column(String(255))
    data_preferences_channels = Column(String(255))
    data_preferences_payments = Column(String(255))
    data_preferences_brands = Column(String(255))
    data_preferences_fragrances = Column(String(255))
    data_preferences_services = Column(String(255))
    data_preferences_other = Column(String(255))

    data_loyalty_codes = Column(String(255))
    data_loyalty_card_id = Column(String(64))
    data_loyalty_card_name = Column(String(255))
    data_loyalty_card_issuer = Column(String(255))
    data_loyalty_card_points = Column(Float)
    data_loyalty_card_expires = Column(DateTime)

    data_message_id = Column(String(36))
    data_message_conversation = Column(String(36))
    data_message_type = Column(String(32))
    data_message_text = Column(String(255))
    data_message_sender = Column(String(96))
    data_message_recipient = Column(String(96))
    data_message_status = Column(String(64))
    data_message_error_reason = Column(String(256))
    data_message_aux = Column(JSON)

    data_ec_order_id = Column(String(64))
    data_ec_order_status = Column(String(32))
    data_ec_order_receivable_value = Column(Float)
    data_ec_order_receivable_due_date = Column(DateTime)
    data_ec_order_receivable_currency = Column(String(255))
    data_ec_order_payable_value = Column(Float)
    data_ec_order_payable_due_date = Column(DateTime)
    data_ec_order_payable_currency = Column(String(255))
    data_ec_order_income_value = Column(Float)
    data_ec_order_income_due_date = Column(DateTime)
    data_ec_order_income_currency = Column(String(255))
    data_ec_order_cost_value = Column(Float)
    data_ec_order_cost_due_date = Column(DateTime)
    data_ec_order_cost_currency = Column(String(255))
    data_ec_order_affiliation = Column(String(32))

    data_ec_checkout_id = Column(String(64))
    data_ec_checkout_status = Column(String(32))
    data_ec_checkout_currency = Column(String(8))
    data_ec_checkout_value = Column(Float)

    data_ec_product_id = Column(String(64))
    data_ec_product_name = Column(String(255))
    data_ec_product_sku = Column(String(32))
    data_ec_product_category = Column(String(64))
    data_ec_product_brand = Column(String(96))
    data_ec_product_variant_name = Column(String(255))
    data_ec_product_variant_color = Column(String(48))
    data_ec_product_variant_size = Column(String(16))
    data_ec_product_price = Column(Float)
    data_ec_product_quantity = Column(Float)
    data_ec_product_position = Column(Integer)
    data_ec_product_review = Column(String(255))
    data_ec_product_rate = Column(Integer)

    data_payment_method = Column(String(255))
    data_payment_credit_card_number = Column(String(24))
    data_payment_credit_card_expires = Column(DateTime)
    data_payment_credit_card_holder = Column(String(64))

    data_journey_state = Column(String(32))
    data_journey_rate = Column(Float)

    data_marketing_coupon = Column(String(255))
    data_marketing_channel = Column(String(255))
    data_marketing_promotion_id = Column(String(64))
    data_marketing_promotion_name = Column(String(64))

    tags_values = Column(String(255))
    tags_count = Column(DOUBLE)

    journey_state = Column(String(32))

    production = Column(Boolean)  # Add this field for multi-tenancy

    # Primary key constraint
    __table_args__ = (
        PrimaryKeyConstraint('id', 'production'),
    )
```

and it to the corresponding object `Event` that has the following schema:

```python
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

from typing import Optional, Dict

from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.geo import Geo
from tracardi.domain.time import Time, ProfileTime


class Metadata(BaseModel):
    time: Time

class ProfileSystemIntegrations(Entity):
    data: Optional[dict] = {}

class ProfileSystemMetadata(BaseModel):
    integrations: Optional[Dict[str, ProfileSystemIntegrations]] = {}
    aux: Optional[dict] = {}
    
    def has_integration(self, system: str) -> bool:
        return system in self.integrations and 'id' in self.integrations[system]
    
    def set_integration(self, system: str, id: str, data:Optional [dict]=None):
        self.integrations[system].id = id
        if data:
            self.integrations[system].data = data

class ProfileMetadata(BaseModel):
    time: ProfileTime
    aux: Optional[dict] = {}
    status: Optional[str] = None
    fields: Optional[dict] = {}
    system: Optional[ProfileSystemMetadata] = ProfileSystemMetadata()

    def set_fields_timestamps(self, field_timestamp_manager):
        for field, timestamp_data  in field_timestamp_manager.get_timestamps():
            self.fields[field] = timestamp_data


class OS(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None


class Device(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    type: Optional[str] = None
    touch: Optional[bool] = False
    ip: Optional[str] = None
    resolution: Optional[str] = None
    geo: Optional[Geo] = Geo.model_construct()
    color_depth: Optional[int] = None
    orientation: Optional[str] = None


class Application(BaseModel):
    type: Optional[str] = None  # Browser, App1
    name: Optional[str] = None
    version: Optional[str] = None
    language: Optional[str] = None
    bot: Optional[bool] = False
    resolution: Optional[str] = None


class Hit(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    referer: Optional[str] = None
    query: Optional[str] = None
    category: Optional[str] = None

    
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

    # device: Optional[dict] = {}
    device: Optional[Device] = Device.construct()

    # os: Optional[dict] = {}
    os: Optional[OS] = OS.construct()

    # app: Optional[dict] = {}
    app: Optional[Application] = Application.construct()

    # hit: Optional[dict] = {}
    hit: Optional[Hit] = Hit.construct()

    journey: EventJourney = EventJourney.model_construct()
    # journey: Optional[dict] = {}

    # data: Optional[dict] = {}
    data: Optional[EventData] = EventData.construct()

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


```

create function `map_to_<object-name>table` that maps domain object to sqlalchemy table. And function `map_to_<object-name>` that
converts table values to domain object. Return only mapping functions, Do not printout the Table or Object definitions. 