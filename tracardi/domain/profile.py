import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Set, Union
from pydantic import BaseModel
from tracardi.service.notation.dot_accessor import DotAccessor
from .entity import Entity
from .geo import Geo
from .metadata import ProfileMetadata
from .storage_record import RecordMetadata
from .time import ProfileTime
from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo
from ..service.dot_notation_converter import DotNotationConverter
from .profile_stats import ProfileStats
from .segment import Segment
from ..process_engine.tql.condition import Condition


def force_lists(props: List[str], data):
    for prop in props:
        if prop in data and data[prop] is not None and not isinstance(data[prop], list):
            data[prop] = [str(data[prop])]
    return data


class ConsentRevoke(BaseModel):
    revoke: Optional[datetime] = None


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


class Profile(Entity):
    ids: Optional[List[str]] = []
    metadata: Optional[ProfileMetadata] = ProfileMetadata(time=ProfileTime(insert=datetime.utcnow()))
    operation: Optional[Operation] = Operation()
    stats: ProfileStats = ProfileStats()
    traits: Optional[dict] = {}
    segments: Optional[List[str]] = []
    interests: Optional[dict] = {}
    consents: Optional[Dict[str, ConsentRevoke]] = {}
    active: bool = True
    aux: Optional[dict] = {}
    data: Optional[ProfileData] = ProfileData()

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._add_id_to_ids()

    def serialize(self):
        return {
            "profile": self.dict(),
            "storage": self.get_meta_data().dict()
        }

    @staticmethod
    def deserialize(serialized_profile: dict) -> 'Profile':
        profile = Profile(**serialized_profile['profile'])
        profile.set_meta_data(RecordMetadata(**serialized_profile['storage']))
        return profile

    def replace(self, profile: 'Profile'):
        if isinstance(profile, Profile):
            # Make segments unique
            profile.segments = list(set(profile.segments))

            self.id = profile.id
            self.ids = profile.ids
            self.metadata = profile.metadata
            self.operation = profile.operation
            self.stats = profile.stats
            self.traits = profile.traits
            self.segments = profile.segments
            self.consents = profile.consents
            self.active = profile.active
            self.interests = profile.interests
            self.aux = profile.aux
            self.data = profile.data

    def get_merge_key_values(self) -> List[tuple]:
        converter = DotNotationConverter(self)
        return [converter.get_profile_file_value_pair(key) for key in self.operation.merge]

    def _get_merging_keys_and_values(self):
        merge_key_values = self.get_merge_key_values()

        # Add keyword
        merge_key_values = [(field, value) for field, value in merge_key_values if value is not None]

        return merge_key_values

    def _add_id_to_ids(self):
        if self.id not in self.ids:
            self.ids.append(self.id)
            self.operation.update = True

    def get_consent_ids(self) -> Set[str]:
        return set([consent_id for consent_id, _ in self.consents.items()])

    async def segment(self, event_types, load_segments):

        """
        This method mutates current profile. Loads segments and adds segments to current profile.
        """

        # todo cache segments for 30 sec
        flat_profile = DotAccessor(
            profile=self
            # it has access only to profile. Other data is irrelevant because we check only profile.
        )

        for event_type in event_types:  # type: str

            # Segmentation is run for every event

            # todo segments are loaded one by one - maybe it is possible to load it at once
            # todo segments are loaded event if they are disabled. It is checked later. Maybe we can filter it here.
            segments = await load_segments(event_type, limit=500)

            for segment in segments:

                segment = Segment(**segment)

                if segment.enabled is False:
                    continue

                segment_id = segment.get_id()

                try:
                    condition = Condition()
                    if await condition.evaluate(segment.condition, flat_profile):
                        segments = set(self.segments)
                        segments.add(segment_id)
                        self.segments = list(segments)

                        # Yield only if segmentation triggered
                        yield event_type, segment_id, None

                except Exception as e:
                    msg = 'Condition id `{}` could not evaluate `{}`. The following error was raised: `{}`'.format(
                        segment_id, segment.condition, str(e).replace("\n", " "))

                    yield event_type, segment_id, msg

    def increase_visits(self, value=1):
        self.stats.visits += value
        self.operation.update = True

    def increase_views(self, value=1):
        self.stats.views += value
        self.operation.update = True

    def increase_interest(self, interest, value=1):
        if interest in self.interests:
            self.interests[interest] += value
        else:
            self.interests[interest] = value
        self.operation.update = True

    def decrease_interest(self, interest, value=1):
        if interest in self.interests:
            self.interests[interest] -= value
            self.operation.update = True

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'profile',
            Profile,
            exclude={"operation": ...},
            multi=True
        )

    @staticmethod
    def new() -> 'Profile':
        """
        @return Profile
        """
        return Profile(
            id=str(uuid.uuid4()),
            metadata=ProfileMetadata(time=ProfileTime(insert=datetime.utcnow()))
        )
