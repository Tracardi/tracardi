from datetime import datetime
from typing import Optional, Union, List, Any
from pydantic import BaseModel
from tracardi.domain.geo import Geo


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
    name: Optional[str] = None
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


class ProfileContactAddress(BaseModel):
    town: Optional[str] = None
    county: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    street: Optional[str] = None
    other: Optional[str] = None


class ProfileContact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    app: Optional[ProfileContactApp] = ProfileContactApp()
    address: Optional[ProfileContactAddress] = ProfileContactAddress()
    confirmations: List[str] = []


class ProfileIdentifier(BaseModel):
    id: Optional[str] = None
    badge: Optional[str] = None
    passport: Optional[str] = None
    credit_card: Optional[str] = None
    token: Optional[str] = None
    coupons: Optional[List[str]] = None


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
    ltcosc: Optional[int] = 0   # Live Time Check-Out Started Counter
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
    names: Optional[List[str]] = []
    last: Optional[LastGeo] = LastGeo()


class ProfileData(BaseModel):
    pii: Optional[ProfilePII] = ProfilePII()
    contact: Optional[ProfileContact] = ProfileContact()
    identifier: Optional[ProfileIdentifier] = ProfileIdentifier()
    devices: Optional[ProfileDevices] = ProfileDevices()
    media: Optional[ProfileMedia] = ProfileMedia()
    preferences: Optional[ProfilePreference] = ProfilePreference()
    job: Optional[ProfileJob] = ProfileJob()
    metrics: Optional[ProfileMetrics] = ProfileMetrics()
    loyalty: Optional[ProfileLoyalty] = ProfileLoyalty()