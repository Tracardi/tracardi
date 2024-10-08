from datetime import datetime
from typing import Optional, Union, List, Any
from pydantic import BaseModel
from tracardi.domain.geo import Geo

# Settings For Auto Profile Merging (APM)

PREFIX_EMAIL_MAIN = "emm-"
PREFIX_EMAIL_BUSINESS =  "emb-"
PREFIX_EMAIL_PRIVATE =  "emp-"
PREFIX_PHONE_MAIN = "phm-"
PREFIX_PHONE_BUSINESS = "phb-"
PREFIX_PHONE_MOBILE = "pho-"
PREFIX_PHONE_WHATSUP = "pwa-"
PREFIX_IDENTIFIER_ID = "iid-"
PREFIX_IDENTIFIER_PK = "ipk-"

PREFIX_PHONE_FIELDS = 'data.contact.phone'
PREFIX_EMAIL_FIELDS = 'data.contact.mail'

FIELD_TO_PROPERTY_MAPPING = {
    'profile@data.identifier.pk': lambda profile: (profile.data.identifier.pk, PREFIX_IDENTIFIER_PK),
    'profile@data.identifier.id': lambda profile: (profile.data.identifier.id, PREFIX_IDENTIFIER_ID),

    'profile@data.contact.phone.main': lambda profile: (profile.data.contact.phone.main, PREFIX_PHONE_MAIN),
    'profile@data.contact.phone.business': lambda profile: (profile.data.contact.phone.business,PREFIX_PHONE_BUSINESS),
    'profile@data.contact.phone.whatsapp': lambda profile: (profile.data.contact.phone.whatsapp,PREFIX_PHONE_WHATSUP),
    'profile@data.contact.phone.mobile': lambda profile: (profile.data.contact.phone.mobile,PREFIX_PHONE_MOBILE),

    'profile@data.contact.email.main': lambda profile: (profile.data.contact.email.main,PREFIX_EMAIL_MAIN),
    'profile@data.contact.email.private': lambda profile: (profile.data.contact.email.private, PREFIX_EMAIL_PRIVATE),
    'profile@data.contact.email.business': lambda profile: (profile.data.contact.email.business, PREFIX_EMAIL_BUSINESS),
}

FLAT_PROFILE_FIELD_MAPPING = {
    'data.identifier.pk': PREFIX_IDENTIFIER_PK,
    'data.identifier.id': PREFIX_IDENTIFIER_ID,

    'data.contact.phone.main': PREFIX_PHONE_MAIN,
    'data.contact.phone.business': PREFIX_PHONE_BUSINESS,
    'data.contact.phone.whatsapp':PREFIX_PHONE_WHATSUP,
    'data.contact.phone.mobile': PREFIX_PHONE_MOBILE,

    'data.contact.email.main': PREFIX_EMAIL_MAIN,
    'data.contact.email.private': PREFIX_EMAIL_PRIVATE,
    'data.contact.email.business': PREFIX_EMAIL_BUSINESS,
}

FLAT_PROFILE_MAPPING = {
    'data.identifier.pk': lambda flat_profile: (flat_profile.get('data.identifier.pk', None), PREFIX_IDENTIFIER_PK),
    'data.identifier.id': lambda flat_profile: (flat_profile.get('data.identifier.id', None), PREFIX_IDENTIFIER_ID),

    'data.contact.phone.main': lambda flat_profile: (flat_profile.get('data.contact.phone.main', None), PREFIX_PHONE_MAIN),
    'data.contact.phone.business': lambda flat_profile: (flat_profile.get('data.contact.phone.business', None), PREFIX_PHONE_BUSINESS),
    'data.contact.phone.whatsapp': lambda flat_profile: (flat_profile.get('data.contact.phone.whatsapp', None), PREFIX_PHONE_WHATSUP),
    'data.contact.phone.mobile': lambda flat_profile: (flat_profile.get('data.contact.phone.mobile', None), PREFIX_PHONE_MOBILE),

    'data.contact.email.main': lambda flat_profile: (flat_profile.get('data.contact.email.main', None), PREFIX_EMAIL_MAIN),
    'data.contact.email.private': lambda flat_profile: (flat_profile.get('data.contact.email.private', None), PREFIX_EMAIL_PRIVATE),
    'data.contact.email.business': lambda flat_profile: (flat_profile.get('data.contact.email.business', None), PREFIX_EMAIL_BUSINESS),
}

def force_lists(props: List[str], data):
    for prop in props:
        if prop in data and data[prop] is not None and not isinstance(data[prop], list):
            data[prop] = [str(data[prop])]
    return data


class ProfileLanguage(BaseModel):
    native: Optional[str] = None
    spoken: Union[Optional[str], Optional[List[str]]] = None


class ProfileEducation(BaseModel):
    level: Optional[str] = None


class ProfileCivilData(BaseModel):
    status: Optional[str] = None


class ProfileAttribute(BaseModel):
    height: Optional[float] = None
    weight: Optional[float] = None
    shoe_number: Optional[float] = None


class ProfilePII(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    display_name: Optional[str] = None
    birthday: Optional[datetime] = None
    language: Optional[ProfileLanguage] = ProfileLanguage()
    gender: Optional[str] = None
    education: Optional[ProfileEducation] = ProfileEducation()
    civil: Optional[ProfileCivilData] = ProfileCivilData()
    attributes: Optional[ProfileAttribute] = ProfileAttribute()


class ProfileContactApp(BaseModel):
    whatsapp: Optional[str] = None
    discord: Optional[str] = None
    slack: Optional[str] = None
    twitter: Optional[str] = None
    telegram: Optional[str] = None
    wechat: Optional[str] = None
    viber: Optional[str] = None
    signal: Optional[str] = None
    other: Optional[dict] = {}

    def has_contact(self) -> bool:
        return bool(
            self.whatsapp or self.discord or self.slack or self.twitter or
            self.telegram or self.wechat or self.viber or self.signal)


class ProfileContactAddress(BaseModel):
    town: Optional[str] = None
    county: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    street: Optional[str] = None
    other: Optional[str] = None


class ProfilePhone(BaseModel):
    main: Optional[str] = None
    business: Optional[str] = None
    mobile: Optional[str] = None
    whatsapp: Optional[str] = None

    def phone_types(self) -> tuple:
        return PREFIX_PHONE_MAIN, PREFIX_PHONE_BUSINESS, PREFIX_PHONE_MOBILE, PREFIX_PHONE_WHATSUP

    def has_business(self) -> bool:
        return bool(self.business)

    def has_main(self) -> bool:
        return bool(self.main)

    def has_mobile(self) -> bool:
        return bool(self.mobile)

    def has_whatsapp(self) -> bool:
        return bool(self.whatsapp)

class ProfileEmail(BaseModel):
    main: Optional[str] = None
    private: Optional[str] = None
    business: Optional[str] = None

    def email_types(self) -> tuple:
        return PREFIX_EMAIL_MAIN, PREFIX_EMAIL_PRIVATE, PREFIX_EMAIL_BUSINESS

    def has_business(self) -> bool:
        return bool(self.business)

    def has_main(self) -> bool:
        return bool(self.main)

    def has_private(self) -> bool:
        return bool(self.private)

class ProfileContact(BaseModel):
    email: Optional[ProfileEmail] = ProfileEmail()
    phone: Optional[ProfilePhone] = ProfilePhone()
    app: Optional[ProfileContactApp] = ProfileContactApp()
    address: Optional[ProfileContactAddress] = ProfileContactAddress()
    confirmations: List[str] = []

    def has_contact(self) -> bool:
        return (self.has_email()
                or self.has_phone()
                or self.app.has_contact())

    def has_email(self) -> bool:
        return bool(self.email.main or self.email.business or self.email.private)

    def has_phone(self) -> bool:
        return bool(self.phone.main or self.phone.business or self.phone.mobile or self.phone.whatsapp)

class ProfileIdentifier(BaseModel):
    id: Optional[str] = None
    pk: Optional[str] = None
    badge: Optional[str] = None
    passport: Optional[str] = None
    credit_card: Optional[str] = None
    token: Optional[str] = None
    coupons: Optional[Union[str,List[str]]] = None


class ProfileSocialMedia(BaseModel):
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    linkedin: Optional[str] = None
    reddit: Optional[str] = None
    other: Optional[dict] = {}


class ProfileMedia(BaseModel):
    image: Optional[str] = None
    webpage: Optional[str] = None
    social: Optional[ProfileSocialMedia] = ProfileSocialMedia()


class ProfilePreference(BaseModel):

    def __init__(self, **data: Any):
        data = force_lists(['purchases', 'colors', 'sizes', 'devices', 'channels', 'payments', 'brands', 'fragrances',
                            'services', 'other'], data)
        super().__init__(**data)

    purchases: Optional[List[str]] = []
    colors: Optional[List[str]] = []
    sizes: Optional[List[str]] = []
    devices: Optional[List[str]] = []
    channels: Optional[List[str]] = []
    payments: Optional[List[str]] = []
    brands: Optional[List[str]] = []
    fragrances: Optional[List[str]] = []
    services: Optional[List[str]] = []
    other: Optional[List[str]] = []


class ProfileCompany(BaseModel):
    name: Optional[str] = None
    size: Optional[int] = None
    segment: Union[Optional[str], List[str]] = None
    country: Optional[str] = None


class ProfileJob(BaseModel):
    position: Optional[str] = None
    salary: Optional[float] = None
    type: Optional[str] = None
    company: Optional[ProfileCompany] = ProfileCompany()
    department: Optional[str] = None


class ProfileMetrics(BaseModel):
    ltv: Optional[float] = 0
    ltcosc: Optional[int] = 0  # Live Time Check-Out Started Counter
    ltcocc: Optional[int] = 0  # Live Time Check-Out Completed Counter
    ltcop: Optional[float] = 0  # Live Time Check-Out Percentage
    ltcosv: Optional[float] = 0  # Live Time Check-Out Started Value
    ltcocv: Optional[float] = 0  # Live Time Check-Out Completed Value
    next: Optional[datetime] = None
    custom: Optional[dict] = {}


class ProfileLoyaltyCard(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    issuer: Optional[str] = None
    expires: Optional[datetime] = None
    points: Optional[float] = 0


class ProfileLoyalty(BaseModel):

    def __init__(self, **data: Any):
        data = force_lists(['codes'], data)
        super().__init__(**data)

    codes: Optional[List[str]] = []
    card: Optional[ProfileLoyaltyCard] = ProfileLoyaltyCard()


class LastGeo(BaseModel):
    geo: Optional[Geo] = Geo()


class ProfileDevices(BaseModel):
    push: Optional[List[str]] = []
    other: Optional[List[str]] = []
    last: Optional[LastGeo] = LastGeo()


class ProfileData(BaseModel):
    anonymous: Optional[bool] = None
    pii: Optional[ProfilePII] = ProfilePII()
    contact: Optional[ProfileContact] = ProfileContact()
    identifier: Optional[ProfileIdentifier] = ProfileIdentifier()
    devices: Optional[ProfileDevices] = ProfileDevices()
    media: Optional[ProfileMedia] = ProfileMedia()
    preferences: Optional[ProfilePreference] = ProfilePreference()
    job: Optional[ProfileJob] = ProfileJob()
    metrics: Optional[ProfileMetrics] = ProfileMetrics()
    loyalty: Optional[ProfileLoyalty] = ProfileLoyalty()

    def compute_anonymous_field(self):
        self.anonymous = not self.contact.has_contact()
